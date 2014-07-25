"""
bdosoa - database ORM models
"""

from sqlalchemy import (Column, Index, ForeignKey, Boolean, DateTime, Enum,
                        Integer, String, Text, UniqueConstraint)
from sqlalchemy.orm import relationship

from bdosoa.model.meta import Base
from bdosoa.util import gen_token


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
                                         cascade='all, delete, delete-orphan')


class SubscriptionVersion(Base):
    """Versao de Subscricao (Bilhete de portabilidade)"""

    __tablename__ = 'subscriptionversion'
    __table_args__ = (
        UniqueConstraint('spid', 'subscription_version_id'),
        Index('ix_subscriptionversion_spid_version_id',
              'spid', 'subscription_version_id'),
        Index('ix_subscriptionversion_spid_version_tn',
              'spid', 'subscription_version_tn'),
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
