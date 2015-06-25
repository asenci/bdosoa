"""
bdosoa - database ORM models
"""

from sqlalchemy import (Column, Index, ForeignKey, Boolean, DateTime, Enum,
                        Integer, String, Text, UniqueConstraint)
from sqlalchemy.orm import relationship

from bdosoa.lib.util import gen_token
from bdosoa.model.meta import Base


class ServiceProviderGateway(Base):
    """Provedor de Servico"""

    __tablename__ = 'service_provider_gateway'
    __table_args__ = (
        UniqueConstraint('service_provider_id', 'token'),
    )
    service_provider_id = Column(String, nullable=False, index=True)
    token = Column(String, nullable=False, default=gen_token)
    soap_url = Column(String, nullable=False)
    description = Column(String)
    enabled = Column(Boolean, nullable=False, default=True)

    subscription_versions = relationship('SubscriptionVersion',
                                         backref='service_provider_gateway',
                                         lazy='dynamic',
                                         cascade='all, delete, delete-orphan')

    sync_clients = relationship('SyncClient',
                                backref='service_provider_gateway',
                                lazy='dynamic',
                                cascade='all, delete, delete-orphan')


class SubscriptionVersion(Base):
    """Versao de Subscricao (Bilhete de portabilidade)"""

    __tablename__ = 'subscription_version'
    __table_args__ = (
        UniqueConstraint('service_provider_gateway_id',
                         'subscription_version_id'),
    )

    subscription_version_id = Column(Integer, nullable=False)
    subscription_version_tn = Column(String)
    subscription_recipient_sp = Column(String)
    subscription_recipient_eot = Column(String)
    subscription_activation_timestamp = Column(DateTime)
    subscription_broadcast_timestamp = Column(DateTime)
    subscription_rn1 = Column(String)
    subscription_new_cnl = Column(String)
    subscription_lnp_type = Column(Enum('lspp', 'lisp', name='lnp_type'))
    subscription_download_reason = Column(Enum('new', 'delete', 'modified',
                                               name='download_reason'))
    subscription_line_type = Column(Enum('Basic', 'DDR', 'CNG',
                                         name='line_type'))
    subscription_optional_data = Column(Text)
    subscription_deletion_timestamp = Column(DateTime)

    service_provider_gateway_id = Column(Integer,
                                         ForeignKey(ServiceProviderGateway.id),
                                         nullable=False)

class SyncClient(Base):
    """Cliente de Sincronismo"""

    __tablename__ = 'sync_client'
    __table_args__ = (
        UniqueConstraint('service_provider_gateway_id', 'token'),
    )

    token = Column(String, nullable=False, default=gen_token)
    description = Column(String)
    enabled = Column(Boolean, nullable=False, default=True)

    service_provider_gateway_id = Column(Integer,
                                         ForeignKey(ServiceProviderGateway.id),
                                         nullable=False)

    tasks = relationship('SyncTask', backref='sync_client', lazy='dynamic',
                         cascade='all, delete, delete-orphan')


class SyncTask(Base):
    """Tarefa de sincronismo"""

    __tablename__ = 'sync_task'
    __table_args__ = (
        UniqueConstraint('sync_client_id', 'subscription_version_id'),
    )

    sync_client_id = Column(Integer, ForeignKey(SyncClient.id), nullable=False)

    subscription_version_id = Column(Integer,
                                     ForeignKey(SubscriptionVersion.id),
                                     nullable=False)
