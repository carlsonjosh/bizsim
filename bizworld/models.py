# -*- coding: utf-8 -*-
"""
Created on Tue May 05 05:45:59 2015

@author: Josh
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship

base = declarative_base()

class Industry(base):
    __tablename__ = 'industry'
    
    id = Column(Integer, primary_key=True)
    alias = Column(String)
    
    businesses = relationship('Business', backref="industry")
    demand = relationship('Demand')

class Period(base):
    __tablename__ = 'period'
    
    id = Column(Integer, primary_key=True)
    simyear = Column(Integer)
    simmonth = Column(Integer)
    simweek = Column(Integer)
    simday = Column(Integer)
    
    #business_start = relationship('Business', backref=backref("starttimeid"))
    owner_start = relationship('Owner', backref="start_period")
    supply = relationship('Supply', backref="period")
    demand = relationship('Demand', backref="period")
    inventory = relationship('Inventory', backref="period")

class Owner(base):
    __tablename__ = 'owner'
    
    id = Column(Integer, primary_key=True)
    alias = Column(String)
    email = Column(String)
    whsespace = Column(Integer, server_default=FetchedValue())
    population = Column(Integer, server_default=FetchedValue())
    starttimeid = Column(Integer, ForeignKey('period.id'))
       
    businesses = relationship('Business', backref="owner")
    
class Business(base):
    __tablename__ = 'business'
    
    id = Column(Integer, primary_key=True)
    alias = Column(String)
    industryid = Column(Integer, ForeignKey('industry.id'))
    ownerid = Column(Integer, ForeignKey('owner.id'))
    starttimeid = Column(Integer, ForeignKey('period.id'))
    produnits = Column(Integer, server_default=FetchedValue())
    
    biz_inventory = relationship('Inventory', backref="business")
      
class Inventory(base):
    __tablename__ = 'inventory'
    
    id = Column(Integer, primary_key=True)
    businessid = Column(Integer, ForeignKey('business.id'))
    timeid = Column(Integer, ForeignKey('period.id'))
    units = Column(Integer)
    price = Column(Float)

class Ledger(base):
    __tablename__ = 'ledger'
    
    id = Column(Integer, primary_key=True)
    businessid = Column(Integer, ForeignKey('business.id'))
    timeid = Column(Integer, ForeignKey('period.id'))
    account = Column(String)
    amount = Column(Float)

class Supply(base):
    __tablename__ = 'supply'
    
    id = Column(Integer, primary_key=True)
    timeid = Column(Integer, ForeignKey('period.id'))
    endunits = Column(Integer)
    wipunits = Column(Integer)
    
class Demand(base):
    __tablename__ = 'demand'
    
    id = Column(Integer, primary_key=True)
    timeid = Column(Integer, ForeignKey('period.id'))
    industryid = Column(Integer, ForeignKey('industry.id'))
    multiplier = Column(Float)
