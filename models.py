from sqlalchemy import Integer, Date, DateTime, Boolean, Numeric, ForeignKey, Unicode
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional
from datetime import date, datetime


class Base(DeclarativeBase):
    pass


class Position(Base):
    __tablename__ = 'Должности'

    position: Mapped[str] = mapped_column('должность', Unicode(32), primary_key=True)
    responsibilities: Mapped[str] = mapped_column('обязанности', Unicode(256))

    employees: Mapped[list['Employee']] = relationship(back_populates="position_rel")


class Topic(Base):
    __tablename__ = 'Тематики'

    topic: Mapped[str] = mapped_column('тематика', Unicode(32), primary_key=True)
    expected_audience: Mapped[str] = mapped_column('ожидаемая_аудитория', Unicode(256))

    projects: Mapped[list['Project']] = relationship(back_populates="topic_rel")


class Employee(Base):
    __tablename__ = 'Сотрудники'

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column('фио', Unicode(64))
    email: Mapped[str] = mapped_column('email', Unicode(32))
    phone: Mapped[str] = mapped_column('телефон', Unicode(11))
    hire_date: Mapped[date] = mapped_column('дата_найма', Date)
    position: Mapped[str] = mapped_column('должность', Unicode(32), ForeignKey('Должности.должность'))
    dismissed: Mapped[bool] = mapped_column('уволен', Boolean)

    position_rel: Mapped['Position'] = relationship(back_populates="employees")
    team_leadership: Mapped[list['Team']] = relationship(back_populates="leader_rel")
    team_participations: Mapped[list['TeamParticipation']] = relationship(back_populates="employee_rel")
    processed_services: Mapped[list['Service']] = relationship(back_populates="processing_employee_rel")
    processed_contracts: Mapped[list['Contract']] = relationship(back_populates="processing_employee_rel")


class Team(Base):
    __tablename__ = 'Команды'

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True)
    team_leader: Mapped[int] = mapped_column('лидер_команды', Integer, ForeignKey('Сотрудники.id'))

    leader_rel: Mapped['Employee'] = relationship(back_populates="team_leadership")
    projects: Mapped[list['Project']] = relationship(back_populates="project_team_rel")
    team_participations: Mapped[list['TeamParticipation']] = relationship(back_populates="team_rel")
    services: Mapped[list['Service']] = relationship(back_populates="implementing_team_rel")


class Project(Base):
    __tablename__ = 'Проект'

    contract: Mapped[Optional[int]] = mapped_column('договор', Integer, ForeignKey('Договор.id'))
    name: Mapped[str] = mapped_column('название', Unicode(32), primary_key=True)
    description: Mapped[Optional[str]] = mapped_column('описание', Unicode(256))
    project_team: Mapped[Optional[int]] = mapped_column('проектная_команда', Integer, ForeignKey('Команды.id'))
    topic: Mapped[Optional[str]] = mapped_column('тематика', Unicode(32), ForeignKey('Тематики.тематика'))
    client: Mapped[int] = mapped_column('клиент', Integer, ForeignKey('Клиент.id'))

    project_team_rel: Mapped[Optional['Team']] = relationship(back_populates="projects")
    topic_rel: Mapped[Optional['Topic']] = relationship(back_populates="projects")
    client_rel: Mapped['Client'] = relationship(back_populates="projects")
    contract_rel: Mapped[Optional['Contract']] = relationship(back_populates="project_rel")
    services: Mapped[list['Service']] = relationship(back_populates="project_rel")


class TeamParticipation(Base):
    __tablename__ = 'Участие_в_команде'

    last_update: Mapped[datetime] = mapped_column('последнее_обновление', DateTime)
    active: Mapped[bool] = mapped_column('активен', Boolean)
    employee: Mapped[int] = mapped_column('сотрудник', Integer, ForeignKey('Сотрудники.id'), primary_key=True)
    team: Mapped[int] = mapped_column('команда', Integer, ForeignKey('Команды.id'), primary_key=True)

    employee_rel: Mapped['Employee'] = relationship(back_populates="team_participations")
    team_rel: Mapped['Team'] = relationship(back_populates="team_participations")


class Service(Base):
    __tablename__ = 'Услуга'

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True)
    processing_employee: Mapped[int] = mapped_column('обрабатывающий_сотрудник', Integer, ForeignKey('Сотрудники.id'))
    application_date: Mapped[date] = mapped_column('дата_обращения', Date)
    payment: Mapped[int] = mapped_column('оплата', Integer, ForeignKey('Оплата.id'))
    project: Mapped[int] = mapped_column('проект', Integer, ForeignKey('Проект.договор'))
    implementing_team: Mapped[int] = mapped_column('реализующая_команда', Integer, ForeignKey('Команды.id'))
    completed: Mapped[bool] = mapped_column('выполнена', Boolean)

    processing_employee_rel: Mapped['Employee'] = relationship(back_populates="processed_services")
    payment_rel: Mapped['Payment'] = relationship(back_populates="service_rel")
    project_rel: Mapped['Project'] = relationship(back_populates="services")
    implementing_team_rel: Mapped['Team'] = relationship(back_populates="services")


class Client(Base):
    __tablename__ = 'Клиент'

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True)
    contact_person: Mapped[str] = mapped_column('контактное_лицо', Unicode(64))
    phone: Mapped[str] = mapped_column('телефон', Unicode(11))
    email: Mapped[str] = mapped_column('email', Unicode(32))

    projects: Mapped[list['Project']] = relationship(back_populates="client_rel")
    contracts: Mapped[list['Contract']] = relationship(back_populates="client_rel")


class Payment(Base):
    __tablename__ = 'Оплата'

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True)
    amount: Mapped[float] = mapped_column('сумма', Numeric(10, 2))
    paid: Mapped[bool] = mapped_column('оплачено', Boolean)

    service_rel: Mapped[Optional['Service']] = relationship(back_populates="payment_rel", uselist=False)
    contract_rel: Mapped[Optional['Contract']] = relationship(back_populates="payment_rel", uselist=False)


class Contract(Base):
    __tablename__ = 'Договор'

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True)
    signing_date: Mapped[date] = mapped_column('дата_подписания', Date)
    implementation_deadline: Mapped[Optional[date]] = mapped_column('срок_реализации', Date)
    processing_employee: Mapped[int] = mapped_column('обрабатывающий_сотрудник', Integer, ForeignKey('Сотрудники.id'))
    client: Mapped[int] = mapped_column('клиент', Integer, ForeignKey('Клиент.id'))
    payment: Mapped[int] = mapped_column('оплата', Integer, ForeignKey('Оплата.id'))

    processing_employee_rel: Mapped['Employee'] = relationship(back_populates="processed_contracts")
    client_rel: Mapped['Client'] = relationship(back_populates="contracts")
    payment_rel: Mapped['Payment'] = relationship(back_populates="contract_rel")
    project_rel: Mapped[Optional['Project']] = relationship(back_populates="contract_rel", uselist=False)