# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 16:28:11 2015

@author: Josh
"""

#import psycopg2
#conn = psycopg2.connect("dbname=bizworld user=Josh")
#cur = conn.cursor()

#cur.execute("INSERT INTO industry (id, alias) VALUES (1,"Agrilculture");")
#cur.execute("SELECT * FROM industry;")
#print cur.fetchone()

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Sequence
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import func, label
import pandas as pd
import numpy as np
import random
from faker import Factory

base = declarative_base()

class Industry(base):
    __tablename__ = 'industry'
    
    id = Column(Integer, primary_key=True)
    alias = Column(String)
    
    businesses = relationship('Business', backref="industry")
    ind_demand = relationship('Demand')

class Period(base):
    __tablename__ = 'period'
    
    id = Column(Integer, primary_key=True)
    simyear = Column(Integer)
    simmonth = Column(Integer)
    simweek = Column(Integer)
    simday = Column(Integer)
    
    business_start = relationship('Busines', backref="biz_start")
    owner_start = relationship('Owner', backref="owner_start")
    supply = relationship('Supply', backref="period_supply")
    demand = relationship('Demand', backref="period_demand")
    inventory = relationship('Inventory', backref="period_inventory")

class Owner(base):
    __tablename__ = 'owner'
    
    id = Column(Integer, primary_key=True)
    alias = Column(String)
    email = Column(String)
    whsespace = Column(Integer)
    population = Column(Integer)
    starttimeid = Column(Integer, ForeignKey('Period.id'))
       
    businesses = relationship('Business', backref='owner')
    
class Business(base):
    __tablename__ = 'business'
    
    id = Column(Integer, primary_key=True)
    alias = Column(String)
    industryid = Column(Integer, ForeignKey('Industry.id'))
    ownerid = Column(Integer, ForeignKey('Owner.id'))
    starttimeid= Column(Integer, ForeignKey('Period.id'))
    produnits = Column(Integer)
    
    inventory = relationship('Inventory', backref="business_inventory")
      
class Inventory(base):
    __tablename__ = 'inventory'
    
    id = Column(Integer, primary_key=True)
    businessid = Column(Integer, ForeignKey('Business.id'))
    timeid = Column(Integer, ForeignKey('Period.id'))
    units = Column(Integer)
    price = Column(Float)

class Ledger(base):
    __tablename__ = 'ledger'
    
    id = Column(Integer, primary_key=True)
    businessid = Column(Integer, ForeignKey('Business.id'))
    timeid = Column(Integer, ForeignKey('Period.id'))
    account = Column(String)
    amount = Column(Float)

class Supply(base):
    __tablename__ = 'supply'
    
    id = Column(Integer, primary_key=True)
    timeid = Column(Integer, ForeignKey('Period.id'))
    endunits = Column(Integer)
    wipunits = Column(Integer)
    
class Demand(base):
    __tablename__ = 'demand'
    
    id = Column(Integer, primary_key=True)
    timeid = Column(Integer, ForeignKey('Period.id'))
    industryid = Column(Integer, ForeignKey('Industry.id'))
    multiplier = Column(Float)

##SQL Alchemy engine and session makers    
engine = create_engine("postgresql+psycopg2://Josh:@localhost/bizworld")
Session = sessionmaker(bind=engine)
session = Session()

##used for adding industries from scratch
def add_industries():
    path = "c:\users\josh\documents\\bizworld"
    industries = pd.read_csv(path + "\\bizworld-industries.csv", index_col=0)
    
    for i in range(len(industries)):
        industry = Industry(id=i+1, alias=industries.values[i][0])
        session.add(industry)
    
    session.commit()
    return "done"    

##used to update periods
def new_period():
    prior = session.query(Period).order_by("Period.id DESC").limit(1).first()
    simyear = prior.simyear
    simmonth = prior.simmonth
    simweek = prior.simweek
    simday = prior.simday
    
    if simday < 7:
        simday += 1
    else:
        simday = 1
        if simmonth % 3 == 0 and simweek < 5:
            simweek += 1
        elif simmonth % 3 <> 0 and simweek < 4:
            simweek += 1
        else:
            simweek = 1
            if simmonth < 12:
                simmonth += 1
            else:
                simmonth = 1
                simyear += 1
    
    new = {
        'year':simyear, 
        'month':simmonth, 
        'week':simweek, 
        'day':simday
        }

    period = Period(simyear=simyear, simmonth=simmonth, simweek=simweek, simday=simday)
    session.add(period)
    session.commit()        
    return new
    
##used to grow population using exponential random number generator with mean of 3%
def pop_growth(pop):
    #should really create a matrix of growth rates based on different factors    
    g = random.expovariate((float(1)/3)*100)
    pop *= (1 + g)
    return pop

def agg_demand(pop, timeid):
    d = np.random.dirichlet(np.ones(13), size=1) #represents the demand probability function of any given industry
    
    ##commit random demand generated to the database
    for i in range(14):
        demand = Demand(timeid=timeid, industryid=i, multiplier=d[i])
        session.add(demand).commit()
    
    ##return a program readable demand matrix
    d = d * pop #should there be a units baseline for each industry?
    df = pd.DataFrame(d, columns=range(1,14), index=['demand']).T
    
    return df

def agg_suppy(timeid):
    result = session.query(Industry.id, func.sum(Business.produnits).label('produnits')).join(Industry.id==Business.industryid).group_by(Industry.id).all()

    #calculate total supply as prod units * 500 + Inventory
    s_new = row.produnits * 500 #should different supply scalars be used for each industry? Should all units be immediately produced?
    ''' still need a way to pull inventory '''    
    
    ##commit supply to the database
    for row in result:
        supply = Supply(timeid=timeid, endunits=s)
        session.add(supply).commit() 
    
    ##return a supply dataframe for program
    df = pd.DataFrame(result)
    return df

def create_owner(starttimeid):
    fn = faker.first_name()
    ln = faker.last_name()
    alias = fn + ' ' + ln    
    email = fn + '.' + ln + '@' + faker.free_email_domain()
    
    owner = Owner(alias=alias, email=email, starttimeid=starttimeid)
    session.add(owner).commit()
    
    return owner

def create_biz(industryid, starttimeid):
    alias = faker.company()
    #industryid = industryid
    #starttimeid = starttimeid
    
    if np.random.randint(1,100) < 10:
        ownerid = random.sample(session.query(Owner.id).all(), 1)
    else:
        create_owner(starttimeid)
        ownerid = session.query(Owner.id).order_by("Owner.id DESC").first()
    
    biz = Business(alias=alias, ownerid=ownerid, industryid=industryid, starttimeid=starttimeid)
    session.add(biz).commit()
    
    return biz

faker = Factory.create()
print faker.first_name()
    
##create one user and business to start with (using a random industry)
if session.query(Business.id).count() == 0:
    cur_timeid = 1
    rnd_industryid = random.choice(session.query(Industry.id).all())
    create_biz(rnd_industryid, cur_timeid)

##core loop of simulation...
for i in xrange(5):
    #
    ##set the current timeid for the simulation...    
    try:
        cur_timeid = session.query(Period.id).filter(Period.id==i).scalar()
    except NoResultFound:
        new_period()
        cur_timeid = session.query(Period.id).filter(Period.id==i).scalar()
    
    ##find the current population as of the current time...    
    population = session.query(func.sum(Owner.population)
    #print population    
    
    ##calculate supply and demand as of the current time...
    #d = agg_demand(population, cur_timeid)
    #s = agg_suppy(cur_timeid)
    #df = pd.DataFrame([d, s], columns=["demand","supply"])    
    
    ##equate supply to demand and identify market price
    #for i in xrange(14):
    #    demand = d[i]
    #    supply = s[i]
    #    price = demand / supply #this equates price to $1 per unit, is this the right approach?
    
    ##identify industries that need new business based on higher demand and open those businesses
    #for industry in d.index:
    #    gap = s[industry] - d[industry]
    #    if gap < 0:
    #        create_biz(industry, cur_timeid)
        
        #in cases where there is sufficient demand, run through business needs...        
    #    else:            
            ##identify revenue for each business
    #        biz_list = list(session.query(Business.id).filter(Business.industryid==industry).all())
    #        biz_list = np.random.shuffle(biz_list)
            
    #        total_demand = d.sum()
    #        i = 0
    #        while total_demand > 0 and i <= len(biz_list):
    #            try:
    #                biz_produnits = session.query(Business.produnits).filter(Business.id==biz_list[i]).scalar()
    #                supply = biz_produnits * 500
                ##do nothing if there are no businesses to 
    #            except len(biz_list) == 0:
    #                break
    #            else:
                    ##check to ensure that there is sufficient demand to meet supply of given business
    #                if total_demand - supply > 0:
    #                    revenue = supply * price[i]
    #                    ledger = Ledger(businessid=biz_list[i], timeid=cur_timeid, account='revenue', amount=revenue)
    #                    session.add(ledger).commit()
                        
                        ##change while loop scalars...
    #                    total_demand = total_demand - supply                    
    #                    i = i + 1
                    #where there is insufficient demand, calculate remaining revenue for current business then store the rest of the inventory
    #                else:
    #                    revenue = total_demand * price[i]
    #                    ledger = Ledger(businessid=biz_list[i], timeid=cur_timeid, account='revenue', amount=revenue)
    #                    session.add(ledger).commit()
                        
                        ##store excess inventory
    #                    for n in xrange(len(biz_list) - i, len(biz_list)):
    #                        inventory = Inventory(businessid=biz_list[n], timeid=cur_timeid, units=total_demand, amount=price[n])
    #                        session.add(inventory).commit()
    #                    break
                    
               
    #yield population