from bdosoa.models.meta import Base
from bdosoa.utils import gen_token
from sqlalchemy import Column, Index, ForeignKey
from sqlalchemy import BigInteger, Boolean, DateTime, Enum, Integer, String
from sqlalchemy import Text
from sqlalchemy.orm import relationship


class ServiceProvider(Base):
    """Provedor de Servico"""

    __tablename__ = 'serviceprovider'
    __table_args__ = (
        Index('ix_serviceprovider_spid_enabled',
              'spid', 'enabled'),
        Index('ix_serviceprovider_spid_token_enabled',
              'spid', 'token', 'enabled'),
    )
    __mapper_args__ = {
        'order_by': 'spid'
    }

    spid = Column(String, unique=True, index=True)
    token = Column(String, default=gen_token)
    enabled = Column(Boolean, default=True)
    spg_url = Column(String)
    sync_url = Column(String)

    messages = relationship('Message', backref='service_provider',
                            cascade='all, delete, delete-orphan')

    subscription_versions = relationship('SubscriptionVersion',
                                         backref='service_provider',
                                         cascade='all, delete, delete-orphan')


class Message(Base):
    """Log de Mensagens"""

    __tablename__ = 'message'
    __mapper_args__ = {
        'order_by': 'id'
    }

    service_provider_id = Column(String, ForeignKey('serviceprovider.spid'))
    invoke_id = Column(BigInteger)
    message_date_time = Column(DateTime)
    message_body = Column(Text)
    done = Column(Boolean, index=True, default=False)
    error = Column(Boolean, default=False)
    error_info = Column(Text, default='')


class SubscriptionVersion(Base):
    """Versao de Subscricao (Bilhete de portabilidade)"""

    __tablename__ = 'subscriptionversion'
    __table_args__ = (
        Index('ix_subscriptionversion_spid_deletion_version_tn',
              'service_provider_id', 'subscription_deletion_timestamp',
              'subscription_version_tn'),
        Index('ix_subscriptionversion_spid_version_id',
              'service_provider_id', 'subscription_version_id'),
    )
    __mapper_args__ = {
        'order_by': ['subscription_version_tn', 'subscription_version_id'],
    }

    service_provider_id = Column(String, ForeignKey('serviceprovider.spid'))
    subscription_version_id = Column(Integer, unique=True)
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
