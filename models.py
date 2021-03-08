from time import time
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from app import db
from flask_login import UserMixin, current_user
from flask import current_app
from util import get_proper_file_content
import enum
import json
from util import encode
from app.search import add_to_index, remove_from_index, query_index
from app.enqueuer import add_element_to_queue, remove_element_from_queue
from flask_sqlalchemy import Pagination

class Status(enum.Enum):
    NOT_PROCESSED = "NOT_PROCESSED"
    PROCESSED = "PROCESSED"
    ERRORED = "ERRORED"
    PROCESSING = "PROCESSING"

class IsActive(enum.Enum):
    V = "V"
    F = "F"

class ScheduledJobStatus(enum.Enum):
    NOT_PROCESSED = 'NOT_PROCESSED'
    COMPLETED = 'COMPLETED'
    N_REPEAT_LEFT = 'N_REPEAT_LEFT'
    PROCESSING = 'PROCESSING'

class BotJobType(enum.Enum):
    IMMEDIATE = 'IMMEDIATE'
    SCHEDULED = 'SCHEDULED'

class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page, filter=None):
        """search for full text 
        
        Parameters
        ----------
        cls: str
            the class to search
        expression: str
            the search query or search expressions
        """
        ids, total = query_index(
            cls.__tablename__,
            expression, 
            page,
            int(per_page)
        )
        if total == 0:
            pagination = Pagination(query=None, page=page, per_page=per_page, 
                                total=total, items = cls.query.filter_by(id=0))
            return pagination,0
        when = []
        for i in range(len(ids)):
            when.append((ids[i],i))
        
        if filter:
            results = cls.query.filter(cls.id.in_(ids)
                                        ,cls.id.in_(filter)
                                        ,cls.is_active == IsActive.V if hasattr(cls,'is_active') else 1 == 1) \
                        .order_by(db.case(when,value=cls.id))
        else:
            results = cls.query.filter(cls.id.in_(ids)
                                        ,cls.is_active == IsActive.V if hasattr(cls,'is_active') else 1 == 1
                                    ).order_by(db.case(when,value=cls.id))
        pagination = Pagination(query=None, page=page, per_page=per_page, 
                                total=total, items = results.all())
        return pagination, total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                if isinstance(obj, BaseIsActiveMixin):
                    if obj.is_active == IsActive.F:
                        remove_from_index(obj.__tablename__, obj)
                    else:
                        add_to_index(obj.__tablename__, obj)
                else:
                    add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        query = cls.query if not hasattr(cls, 'is_active') else cls.query.filter(cls.is_active==IsActive.V)
        for obj in query:
            add_to_index(cls.__tablename__, obj)

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

class BaseMixin(db.Model):
    __abstract__ = True
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.Integer)
    ovn = db.Column(db.Integer,default=1)

class BaseIsActiveMixin(BaseMixin):
    __abstract__ = True
    is_active = db.Column(db.Enum(IsActive), nullable=False, default=IsActive.V)
    
    def delete(self):
        self.is_active = IsActive.F
        self.updated_date = datetime.utcnow()
        self.updated_by = current_user.id
        self.ovn = 1 if self.ovn is None else self.ovn + 1

# New tables to role manager.
class Role(BaseIsActiveMixin):
    __table_args__ = (
        db.CheckConstraint("is_active IN ('V','F')", \
                             name="role_is_active_ck"),
    )
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(10), nullable=False)

    @staticmethod
    def by_id(_id, is_active='V'):
        if is_active is None:
            return Role.query.filter_by(id=_id).first()
        else:
            return Role.query.filter_by(id=_id, is_active=is_active).first()

    @staticmethod
    def all():
        return Role.query.all()

    def __repr__(self):
        return '<Role name: {}, is_active: {}>'.format(self.name, self.is_active)
    
class Permission(BaseIsActiveMixin):
    __table_args__ = (
        db.CheckConstraint("is_active IN ('V','F')", \
                             name="permission_is_active_ck"),
    )
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    code = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return '<Permission code: {}, description: {}, isActive: {}>'.format(self.code, self.description, self.is_active)
    
class PermissionRole(BaseIsActiveMixin):
    __table_args__ = (
        db.CheckConstraint("is_active IN ('V','F')", \
                             name="permission_role_is_active_ck"),
    )
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    permiss_id = db.Column(db.Integer, db.ForeignKey('permission.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

    def __repr__(self):
        return '<PermissionRole permissionId: {}, roleId: {}, isActive: {}>'.format(self.permission_id, self.role_id, self.is_active)

class Contract(BaseIsActiveMixin):
    __table_args__ = (
        db.CheckConstraint("is_active IN ('V','F')", \
                             name="contract_is_active_ck"),
    )
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    file_archived = db.Column(db.String, nullable=False) # Cambiar para que almacene archivos.
    
    def __repr__(self):
        return '<Contract fileArchived: {}, isActive: {}>'.format(self.file_archived, self.is_active)
    
class PkgService(BaseIsActiveMixin):
    __table_args__ = (
        db.CheckConstraint("is_active IN ('V','F')", \
                             name="pkg_service_is_active_ck"),
    )
    __table_args__ = (
        db.CheckConstraint("service_type IN ('PACKAGE','COMPLEMENT')", \
                             name="pkg_service_type_ck"),
    )
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    service_name = db.Column(db.String(50), nullable=False)
    bot_player = db.Column(db.Integer, nullable=False)
    bot_developer = db.Column(db.Integer, nullable=False)
    mission_ctrl = db.Column(db.Integer, nullable=False)
    time_live = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    service_type = db.Column(db.String(10), nullable=False)

    @staticmethod
    def by_id(_id, is_active='V'):
        return PkgService.query.filter_by(id=_id, is_active=is_active).first()
    
    def __repr__(self):
        return '<PkgService serviceName: {}, botPlayer: {}, botDeveloper: {}, missionCtrl: {}, timeLive: {}, cost: {} currency: {}, serviceType: {}, isActive: {}>'\
            .format(self.service_name, self.bot_player, self.bot_developer, self.mission_ctrl, self.time_live, self.cost, self.currency, self.service_type, self.is_active)

class Customer(BaseIsActiveMixin):
    __table_args__ = (
        db.CheckConstraint("is_active IN ('V','F')", \
                             name="customer_is_active_ck"),
    )
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    rfc = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.Integer, nullable=False)

    @staticmethod
    def by_id(_id):
        return Customer.query.filter_by(id=_id, is_active='V').first()
    
    @staticmethod
    def by_email(email):
        return Customer.query.filter_by(email=email, is_active='V').first()
    
    def __repr__(self):
        return '<Customer name: {}, address: {}, email: {}, rfc: {}, phone: {}, isActive: {}>'\
            .format(self.name, self.address, self.email, self.rfc, self.phone, self.is_active)

class Subscription(BaseIsActiveMixin):
    __table_args__ = (
        db.CheckConstraint("is_active IN ('V','F')", \
                             name="subscription_is_active_ck"),
    )
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    parent_contract_id = db.Column(db.Integer, db.ForeignKey('subscription.id'), nullable=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'), nullable=True)
    pkg_service_id = db.Column(db.Integer, db.ForeignKey('pkg_service.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    activation_code = db.Column(db.String(20), nullable=True)
    
    # Calculating deadline
    def set_end_date(self):
        limit_date = str()
        current_date = datetime.now().date()
        limit_day = current_date.day + 10
        if limit_day > 30:
            limit_day = '0' + str(limit_day - 30)
            limit_month = str(current_date.month + 1)
            limit_month = limit_month if len(limit_month) > 1 else '0'+limit_month
            
            if int(limit_month) > 12:
                limit_month = '0' + str(int(limit_month) - 12)
                limit_year = str(current_date.year + 1)
                
                limit_date = limit_year +'-'+ limit_month +'-'+ limit_day
            else:
                limit_date = str(current_date.year) +'-'+ limit_month +'-'+ limit_day
        else:
            month = str(current_date.month)
            month = month if len(month) > 1 else '0'+month
            
            limit_day = str(limit_day)
            limit_day = limit_day if len(limit_day) > 1 else '0'+limit_day
            
            if month == '02' and int(limit_day) > 28:
                month = '03'
                limit_day = '0' + str(int(limit_day) - 28)
            
            limit_date = str(current_date.year) +'-'+ month +'-'+ limit_day
            
        limit_date = datetime.strptime(limit_date, '%Y-%m-%d')
        self.end_date = limit_date
    
    @staticmethod
    def all():
        return Subscription.query.all()

    @staticmethod
    def by_id(_id, is_active='V'):
        return Subscription.query.filter_by(id=_id, is_active=is_active).first()

    @staticmethod
    def by_customer_id(_id):
        return Subscription.query.filter_by(customer_id=_id, is_active='V').first()

    @staticmethod
    def by_activation_code(activation_code):
        return Subscription.query.filter_by(activation_code=activation_code, is_active='V').first()

    @staticmethod
    def set_activationCode_hash(activation_code):
        return generate_password_hash(activation_code)

    def __repr__(self):
        return '<Subscription startDate: {}, endDate: {}, cost: {}, currency: {}, parentContractId: {}, contractId: {}, pkgServiceId: {}, customerId: {}, isActive: {}>'\
            .format(self.start_date, self. end_date, self.cost, self.currency
                                                                  , self.parent_contract_id, self.contract_id, self.pkg_service_id
                                                                  , self.customer_id, self.is_active)
    
class AditionalComplement(BaseIsActiveMixin):
    __table_args__ = (
        db.CheckConstraint("is_active IN ('V','F')", \
                             name="aditional_items_is_active_ck"),
    )
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    pkg_service_id = db.Column(db.Integer, db.ForeignKey('pkg_service.id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.id'), nullable=False)
    
    def __repr__(self):
        return '<AditionalComplement quantity: {}, cost: {}, currency: {}, pkServiceId: {}, subscriptionId: {}, isActive: {}>'\
            .format(self.quantity, self.cost, self.currency, self.pkg_service_id, self.subscription_id, self.is_active)

class User(BaseIsActiveMixin, UserMixin):
    """defines the `user` table

    Attributes
    ----------
    user_secret: str
        the user secret identifier
    first_name: str
        user first name
    last_name: str
        user last name
    email: str
        user email
    password_hash: str
        password hashed value
    is_active: Enum IsActive (V and F values)

    Methods
    -------
    set_password()

    """

    __table_args__ = (
        db.CheckConstraint("is_active IN ('V','F')", name="user_is_active_ck"),
        db.CheckConstraint("confirm_email IN ('V','F')", name="confirm_email_ck"),
    )

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_secret	= db.Column(db.String(100), index=True, unique=True, nullable=False)
    first_name 	= db.Column(db.String(50) , nullable=False)
    last_name = db.Column(db.String(100) , nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(100) , nullable=False)
    #addresses = db.relationship('Address', backref='user', cascade='save-update')
    bots = db.relationship("Bot", backref="user", lazy='dynamic')
    task = db.relationship('Task', backref='user',lazy='dynamic')
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.id'), nullable=True)
    confirm_email = db.Column(db.String(1), nullable=False, default='F')

    def __repr__(self):
        return '<User first Name: {}, last Name: {}, email: {}, is_active: {}>' \
                .format(self.first_name, self.last_name, self.email, self.is_active)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    # Method to send encript email
    @staticmethod
    def set_email_hash(email_hash):
        user_id = email_hash.split('-')[0]
        long_email = int(email_hash.split('|')[0].split('-')[1])
        user_hash = email_hash.split('|')[1]

        email = user_hash[:long_email]
        email = generate_password_hash(email)
        passwd_hash = user_hash[long_email:]

        return user_id + '-' + str(len(email)) + '|' + email + passwd_hash

    # Method to check email confirm
    def check_email_hash(self, email_hash):
        return check_password_hash(email_hash, self.email)

    def set_user_secret(self, secret):
        self.user_secret = encode(secret)

    def check_password(self,password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def check_password_to_change(passwd_hash,password):
        return check_password_hash(passwd_hash, password)
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in}
            , current_app.config['SECRET_KEY']
            , algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def get_tasks(self, page=1):
        user_tasks = Task.query.filter(Task.user_id == current_user.id, 
                            Task.is_active == 'V') \
        .order_by(Task.is_public.desc(), Task.id.desc()) \
        .paginate(page=page,per_page=current_app.config['TASK_PER_PAGE'])
        return user_tasks

    def get_tasks_public(self, page=1):
        users = User.by_subscription_id(subscription_id=current_user.subscription_id, all=True)
        users_id = []
        for user in users: users_id.append(user.id)

        tasks_public = Task.query.filter(Task.user_id.in_(users_id), Task.is_public == 'V', Task.is_active == 'V') \
        .order_by(Task.is_public.desc(), Task.id.desc()) \
        .paginate(page=page,per_page=current_app.config['TASK_PER_PAGE'])

        return tasks_public

    @staticmethod
    def get_tasks_player(self, user_id, page=1):
        user_tasks = Task.query.filter(Task.user_id == user_id, 
                            Task.is_active == 'V') \
        .order_by(Task.id.desc()) \
        .paginate(page=page,per_page=current_app.config['TASK_PER_PAGE'])
        return user_tasks

    def confirm_email_user(self):
        try:
            if self.confirm_email == 'F':
                self.confirm_email = 'V'
                db.session.commit()
            else:
                self.confirm_email = 'F'
                db.session.commit()
            return True
        except:
            db.sessino.rollback()
            return False

    @staticmethod
    def all():
        return User.query.all()

    @staticmethod
    def by_id(_id, is_active='V'):
        if is_active == None:
            return User.query.filter_by(id=_id).first()
        return User.query.filter_by(id=_id, is_active=is_active).first()
    
    @staticmethod
    def by_email(email, is_active='V'):
        if is_active == None:
            return User.query.filter_by(email=email).first()
        return User.query.filter_by(email=email, is_active=is_active).first()
    
    @staticmethod
    def by_user_secret(user_secret, is_active='V'):
        return db.session.query(User).filter(User.user_secret==user_secret, is_active==is_active).first()
        #return User.query.filter_by().first()

    @staticmethod
    def by_subscription_id(subscription_id, all=False, is_active='V'):
        if all and is_active == 'V':
            return User.query.filter_by(subscription_id=subscription_id, is_active=is_active).all()
        elif all and is_active == None:
            return User.query.filter_by(subscription_id=subscription_id).all()
        else:
            return User.query.filter_by(subscription_id=subscription_id, is_active=is_active).first()

    @staticmethod
    def edit_first_name(_id, new_name):
        try:
            user = User.by_id(_id=_id)
            user.first_name = new_name
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False

    @staticmethod
    def edit_last_name(_id, new_name):
        try:
            user = User.by_id(_id=_id)
            user.last_name = new_name
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False

    @staticmethod
    def edit_password_hash(_id, new_passwd):
        try:
            user = User.by_id(_id=_id)
            user.set_password(new_passwd)
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False

    @staticmethod
    def deactivate(user):
        try:
            user.is_active = 'F'
            user.confirm_email = 'F'
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False

    @staticmethod
    def activate(user):
        try:
            user.is_active = 'V'
            user.password_hash = 'RESET'
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False

class UserRole(BaseIsActiveMixin):
    __table_args__ = (
        db.CheckConstraint("is_active IN ('V','F')", \
                             name="user_role_is_active_ck"),
    )
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

    @staticmethod
    def by_id(_id):
        return UserRole.query.filter_by(id=_id, is_active='V').first()

    @staticmethod
    def by_user_id(user_id, is_active='V'):
        if is_active is None:
            return UserRole.query.filter_by(user_id=user_id).first()
        else:
            return UserRole.query.filter_by(user_id=user_id, is_active=is_active).first()

    @staticmethod
    def change_role_admin(new_user_admin, current, new_rol_current):
        try:
            new_user_admin = UserRole.by_user_id(new_user_admin.id)
            current = UserRole.by_user_id(current.id)

            current.role_id = new_rol_current
            new_user_admin.role_id = 1
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False

    @staticmethod
    def deactivate(user_role):
        try:
            user_role.is_active = 'F'
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False

    @staticmethod
    def activate(user_role):
        try:
            user_role.is_active = 'V'
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False
    
    def __repr__(self):
        return '<UserRole userId: {}, roleId: {}, isActive: {}>'.format(self.user_id, self.role_id, self.is_active)

class Invitation(BaseIsActiveMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    admin_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    guess = db.Column(db.String(100), nullable=False)
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id'), nullable=False)
    invitation_code = db.Column(db.String(100), nullable=False)
    activation_code_hash = db.Column(db.String(100), nullable=False)

    @staticmethod
    def by_invitation(code):
        return Invitation.query.filter_by(invitation_code=code, is_active='V').first()

    @staticmethod
    def _add(invitation):
        try: 
            db.session.add(invitation)
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False

    def __repr__(self):
        return '<Inivitation admin_id: {}, guess: {}>'.format(self.admin_id, self.guess)

class Address(BaseIsActiveMixin):

    __table_args__ = (
        db.CheckConstraint("is_active IN ('V','F')", name="address_is_active_ck"),
    )

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    municipality = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(300), nullable=False)
    postal_code	= db.Column(db.String(5), nullable=False)
    interior_number	= db.Column(db.String(10), nullable=False)
    exterior_number	= db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return "<Adress city: {}, state: {}, municipality: {}, street: {}, postalCode: {}, isActive: {}> " \
            .format(self.city, self.state, self.municipality, self.street, self.postal_code, self.is_active)

class Bot(SearchableMixin, BaseIsActiveMixin):

    __searchable__ = ['name','description','user_id']
    __table_args__ = (
        db.CheckConstraint("is_active IN ('V','F')", name="bot_is_active_ck"),
    )

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bot_secret = db.Column(db.String(100), nullable=False)	
    botJob = db.relationship('BotJob', backref='bot',lazy='dynamic')
    task = db.relationship('BotTask', backref='bot', lazy='dynamic')
    scheduled_job = db.relationship('BotScheduledJob', backref='bot', lazy='dynamic')

    def set_bot_secret(self, bot_secret):
        self.bot_secret = encode(bot_secret)

    @property
    def is_connected(self):
        return len(db.session.query(BotHeartbeat.bot_id).filter(
            BotHeartbeat.registered_at >=  datetime.utcnow()+ timedelta(seconds= -31)
            ,BotHeartbeat.bot_id == self.id
        ).all()) > 0

    @property
    def total_of_tasks(self):
        return db.session.query(db.func.count(BotTask.id)) \
                .filter(BotTask.bot_id == self.id 
                        ,BotTask.is_active == IsActive.V).scalar()

    @property
    def total_of_scheduled(self):
        return db.session.query(db.func.count(BotScheduledJob.id)) \
                .filter(BotScheduledJob.bot_id == self.id 
                        ,BotScheduledJob.is_active == IsActive.V).scalar()

    def get_tasks(self, page):
        bot_tasks = BotTask.query.filter(
            BotTask.bot_id == self.id, 
            BotTask.is_active == IsActive.V
        ).subquery()
        tasks = db.session.query(Task).filter(Task.is_active == IsActive.V) \
            .join(bot_tasks, bot_tasks.c.task_id == Task.id)\
            .order_by(Task.id.desc())
        return tasks.paginate(page=page,per_page=current_app.config['TASK_PER_PAGE'])

    def delete(self):
        super().delete()
        jobs = BotScheduledJob.query.filter(BotScheduledJob.bot_id == self.id).all()
        for job in jobs:
            job.delete()

    @staticmethod
    def add_bot(bot):
        try :
            db.session.add(bot)
            db.session.commit()
            return 'Bot added successfully.'
        except: 
            return 'Error adding bot'

    @staticmethod
    def by_id(_id):
        return Bot.query.filter_by(id=_id, is_active='V').first()

    @staticmethod
    def by_user_id(_id, all=False, is_active='V'):
        if all:
            return Bot.query.filter_by(user_id=_id, is_active=is_active).all()
        else:
            return Bot.query.filter_by(user_id=_id, is_active=is_active).first()

    @staticmethod
    def deactivate(user_id):
        try:
            bots = Bot.query.filter_by(user_id=user_id, is_active='V').all()
            for bot in bots:
                bot.is_active = 'F'
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False

    def __repr__(self):
        return '<Bot name: {}, is_active: {}>'.format(self.name, self.is_active)

class BotHeartbeat(BaseMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    bot_id = db.Column(db.Integer, db.ForeignKey('bot.id'))
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<BotHeartbeat bot name: {}, registered at: {}>'.format(self.bot.name,self.registered_at)

class Parameter(BaseIsActiveMixin):

    __table_args__ = (
        db.CheckConstraint("param_type IN ('VARCHAR','NUMBER','DATE')", name="parameter_param_type_ck"),
    )

    parameter_key = db.Column(db.String(50), primary_key=True, nullable=False)
    parameter_desc = db.Column(db.String(200), nullable=False)
    param_type = db.Column(db.String(20), nullable=False, default = 'VARCHAR')
    varchar_value = db.Column(db.String(3000), nullable=True, default = 'VARCHAR')	
    number_value = db.Column(db.Float)
    date_value = db.Column(db.DateTime)

    def get_value(self):
        value = None
        if self.param_type == 'VARCHAR':
            value = self.varchar_value
        elif self.param_type == 'NUMBER':
            value = self.number_value
        elif self.param_type == 'DATE':
            value = self.date_value
        return value

    def __repr__(self):
        return "<Parameter parameter key: {}, param_type: {}, param value {}" \
                .format(self.parameter_key, self.param_type, self.get_value())

class Task(SearchableMixin, BaseIsActiveMixin):

    __searchable__ = ['user_id','name']

    __table_args__ = (
        db.CheckConstraint("is_active IN ('V','F')", name="task_is_active_ck"),
        db.CheckConstraint("is_public IN ('V','F')", name="task_is_public_ck")
    )

    id = db.Column(db.Integer, primary_key=True,nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    name = db.Column(db.String(50),nullable=False)
    taskVersion = db.relationship('TaskVersion', backref='task',lazy='dynamic')
    bot_task = db.relationship('BotTask', backref='task', lazy='dynamic')
    scheduled_job = db.relationship('BotScheduledJob', backref='task', lazy='dynamic')
    is_public = db.Column(db.String(1), nullable=False, default='F')

    def delete(self):
        super().delete()
        jobs = BotScheduledJob.query.filter(BotScheduledJob.task_id == self.id).all()
        for job in jobs:
            job.delete()

    def public(self):
        try:
            self.is_public = 'V'
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False

    def get_scheduled_tasks(self, page = 1):
        return BotScheduledJob.query.filter(BotScheduledJob.task_id==self.id
                                            ,BotScheduledJob.is_active==IsActive.V) \
                .paginate(page=page, per_page=current_app.config['SCHEDULED_TASK_PER_PAGE'])

    def get_execution_details(self, page = 1):
        task_version = db.session.query(TaskVersion.task_id, TaskVersion.id)\
                        .filter(TaskVersion.task_id == self.id).subquery()
        return BotJob.query.filter(BotJob.task_version_id==task_version.c.id) \
                .order_by(BotJob.creation_date.desc()) \
                .paginate(page=page, per_page=current_app.config['TASK_EXEC_DETAILS_PER_PAGE'])

    @property
    def total_of_scheduled(self):
        return db.session.query(db.func.count(BotScheduledJob.id)) \
                                .filter(BotScheduledJob.task_id == self.id 
                                        ,BotScheduledJob.is_active == IsActive.V).scalar()
    
    @staticmethod
    def by_id(_id, is_active='V'):
        return Task.query.filter_by(id=_id, is_active=is_active).first()

    @staticmethod
    def by_user_id(user_id, all=False, is_active='V'):
        if all:
            return Task.query.filter_by(user_id=user_id, is_active=is_active).all()
        return Task.query.filter_by(user_id=user_id, is_active=is_active).first()

    @staticmethod
    def deactivate(user_id):
        tasks = Task.query.filter_by(user_id=user_id, is_active='V').all()
        print(tasks)
        for task in tasks:
            print(task)
            db.session.delete(task)
        db.session.commit()
        return True

    def __repr__(self):
        return '<Task name {}, is_active {}, user_id {}>'.format(self.name, self.is_active, self.user_id)

class TaskVersion(SearchableMixin, BaseIsActiveMixin):

    __searchable__ = []
    __json__searchable__ = ['task_body']

    __table_args__ = (
        db.CheckConstraint("is_active IN ('V','F')", name="task_version_is_active_ck"),
    )

    id =  db.Column(db.Integer, primary_key=True, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    task_body = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<TaskVersion task_id {}, task_body {}, is_active {}>' \
                .format(self.task_id, self.task_body, self.is_active)

    def set_task_body(self, body, extension):
        task_body = get_proper_file_content(body, extension)
        self.task_body = task_body

class BotJob(BaseMixin):
    __table_args__ = (
        db.CheckConstraint("status IN ('NOT_PROCESSED','PROCESSED','PROCESSING','ERRORED')", \
                             name="bot_job_status_ck"),
    )

    id =  db.Column(db.Integer, primary_key=True, nullable=False)
    bot_id = db.Column(db.Integer,db.ForeignKey('bot.id'),nullable=False)
    task_version_id = db.Column(db.Integer, db.ForeignKey('task_version.id'), nullable=False)
    parameters = db.Column(db.String(100), nullable=True)
    status = db.Column(db.Enum(Status), nullable=False, default = Status.NOT_PROCESSED)
    execution_status = db.Column(db.String(20), nullable=True)
    job_type = db.Column(db.Enum(BotJobType), default= BotJobType.IMMEDIATE)

    def __repr__(self):
        return '<BotJob bot_id {}, task_version_id {}, parameters {}, status {}>' \
                .format(self.bot_id, self.task_version_id, self.parameters, self.status)

class BotJobFailureEvidence(BaseMixin):
    id =  db.Column(db.Integer, primary_key=True, nullable=False)
    bot_job_id = db.Column(db.Integer,db.ForeignKey('bot_job.id'),nullable=False)
    image = db.Column(db.LargeBinary,nullable=False)

    def __repr__(self):
        return '<BotJobFailureEvidence id{}, bot_job_id {}>'

class BotJobEvidence(BaseMixin):

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    bot_job_id = db.Column(db.Integer, db.ForeignKey('bot_job.id'), nullable=False, index=True)
    evidence = db.Column(db.Text, nullable=False)
    extension = db.Column(db.String(10), nullable=False)

class BotTask(BaseIsActiveMixin):
    __table_args__ = (
        db.CheckConstraint("is_active IN ('V','F')", \
                             name="bot_task_is_active_ck"),
    )

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    bot_id = db.Column(db.Integer, db.ForeignKey('bot.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)

    def __repr__(self):
        return '<BotTask id: {}, bot: {}, task: {}>'.format(self.id, self.bot.name, self.task.name)

# Clase a analizar
class BotScheduledJob(BaseIsActiveMixin): # Pendiente a modificar

    __table_args__ = (
        db.CheckConstraint("is_active IN ('V','F')", \
                             name="bot_scheduled_job_is_active_ck"),
        db.CheckConstraint("status IN ('NOT_PROCESSED','COMPLETED','N_REPEAT_LEFT', 'PROCESSING')", \
                             name="bot_scheduled_job_status_ck"),
    )

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    bot_id = db.Column(db.Integer, db.ForeignKey('bot.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False) # task_version_id
    parameters = db.Column(db.String(100))
    status = db.Column(db.Enum(ScheduledJobStatus),nullable=False, default=ScheduledJobStatus.NOT_PROCESSED)
    # Variable when a modificar
    when = db.Column(db.String(100), nullable=False)
    until = db.Column(db.DateTime, nullable=True)
    repeat = db.Column(db.Integer, nullable=True)
    queue_identifier = db.Column(db.String(100),index=True)

    def enqueue(self):
        queueName, periodicity, metadata, isPublish = self.__to_queue()
        self.queue_identifier = add_element_to_queue(queueName, periodicity, metadata, isPublish)
        
    def delete(self):
        super().delete()
        self.dequeue()

    def dequeue(self):
        if self.queue_identifier:
            remove_element_from_queue(self.__get_queue_name(),self.queue_identifier)

    def __to_queue(self):
        queue_name = self.__get_queue_name()
        periodicity = self.when[self.when.find(";") + 1:] if self.when is not None else '1' # # = '1:2020-12-03:2020-12-30/20:23/00:23'
        periodicity = periodicity if len(periodicity) > 0 else '1' # En caso de ser igual a 0, se iguala a 1.
        metadata = "{" + ('"id":%s' % self.id) + "}" 
        isPublish = True

        return (queue_name, periodicity, metadata, isPublish)

    def __get_queue_name(self): # Lo que retorna es igual a la calendarización ('periodicity').
        return self.when[:self.when.find(";")] if self.when is not None else None
    
    def string_rep(self):
        return self.__to_queue()

    def __repr__(self):
        return '<BotScheduledJob id= {}, bot = {}-{}, task: {}-{}, status: {}, when: {}>'\
            .format(self.id, self.bot_id, self.bot.name if self.bot is not None else ''
                    , self.task_id, self.task.name if self.task is not None else ''
                    , self.status, self.when)