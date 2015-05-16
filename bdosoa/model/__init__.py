"""
bdosoa - database ORM models
"""

from sqlalchemy import (Column, Index, ForeignKey, Boolean, DateTime, Enum,
                        Integer, String, Text, UniqueConstraint)
from sqlalchemy.orm import relationship

from bdosoa.lib.util import gen_token
from bdosoa.model.meta import Base


class ServiceProvider(Base):
    """Provedor de Servico"""

    __tablename__ = 'serviceprovider'
    __table_args__ = (
        Index('ix_serviceprovider_spid_enabled',
              'spid', 'enabled'),
        Index('ix_serviceprovider_spid_token_enabled',
              'spid', 'token', 'enabled'),
    )

    spid = Column(String, unique=True, index=True)
    token = Column(String, default=gen_token)
    enabled = Column(Boolean, default=True)
    spg_url = Column(String)

    subscription_versions = relationship('SubscriptionVersion',
                                         backref='service_provider',
                                         lazy='dynamic',
                                         cascade='all, delete, delete-orphan')

    sync_clients = relationship('SyncClient',
                                backref='service_provider',
                                lazy='dynamic',
                                cascade='all, delete, delete-orphan')


class SubscriptionVersion(Base):
    """Versao de Subscricao (Bilhete de portabilidade)"""

    __tablename__ = 'subscriptionversion'
    __table_args__ = (
        UniqueConstraint('spid', 'subscription_version_id'),
        Index('ix_subscriptionversion_spid_version_id',
              'spid', 'subscription_version_id'),
        Index('ix_subscriptionversion_spid_version_tn_deletion_timestamp',
              'spid', 'subscription_version_tn',
              'subscription_deletion_timestamp'),
    )

    spid = Column(String, ForeignKey('serviceprovider.spid'))
    subscription_version_id = Column(Integer)
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


class SyncClient(Base):
    """Cliente de Sincronismo"""

    __tablename__ = 'syncclient'
    __table_args__ = (
        Index('ix_syncclient_spid_enabled',
              'spid', 'enabled'),
        Index('ix_syncclient_spid_token_enabled',
              'spid', 'token', 'enabled'),
    )

    spid = Column(String, ForeignKey('serviceprovider.spid'))
    token = Column(String, default=gen_token)
    enabled = Column(Boolean, default=True)

    tasks = relationship('SyncTask', backref='sync_client', lazy='dynamic',
                         cascade='all, delete, delete-orphan')


class SyncTask(Base):
    """Tarefa de sincronismo"""

    __tablename__ = 'synctask'
    syncclient_id = Column(Integer, ForeignKey('syncclient.id'), index=True)
    subscriptionversion_id = Column(Integer,
                                    ForeignKey('subscriptionversion.id'))
