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
from sqlalchemy import Column, Integer, String, Float, ForeignKey, FetchedValue
from sqlalchemy import create_engine, update
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
    demand = relationship('Demand', backref="industry")
    supply = relationship('Supply', backref="industry")

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
    industryid = Column(Integer, ForeignKey('industry.id'))
    endunits = Column(Integer)
    wipunits = Column(Integer)
    
class Demand(base):
    __tablename__ = 'demand'
    
    id = Column(Integer, primary_key=True)
    timeid = Column(Integer, ForeignKey('period.id'))
    industryid = Column(Integer, ForeignKey('industry.id'))
    multiplier = Column(Float)
    units = Column(Integer)

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

def create_owner(starttimeid):
    fn = faker.first_name()
    ln = faker.last_name()
    alias = fn + ' ' + ln    
    email = fn + '.' + ln + '@' + faker.free_email_domain()
    
    owner = Owner(alias=alias, email=email, starttimeid=starttimeid)
    session.add(owner)
    session.commit()
    
    return owner

def create_biz(industryid, starttimeid):
    alias = faker.company()
    owner_expand = np.random.randint(1,100)
    
    if owner_expand < 10:
        try:        
            ownerid = random.sample(session.query(Owner.id).all(), 1)[0][0]
        except ValueError:
            create_owner(starttimeid)
            ownerid = session.query(Owner.id).order_by("Owner.id DESC").limit(1).scalar()
    else:
        create_owner(starttimeid)
        ownerid = session.query(Owner.id).order_by("Owner.id DESC").limit(1).scalar()
    
    biz = Business(alias=alias, ownerid=ownerid, produnits=1, industryid=industryid, starttimeid=starttimeid)
    session.add(biz)
    session.commit()
    
    return biz

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
    g = random.expovariate((float(1)/5)*100)
    pop *= 1 + (g / 364)

    '''
        1. Should there be a chance of negative population growth?
        2. What would a matrix of population growth factors look like?
    '''    
    
    return pop

def agg_demand(pop, timeid):
    d = np.random.dirichlet(np.ones(13), size=1) #represents the demand probability function of any given industry
    
    ##commit random demand generated to the database
    for i in xrange(13):
        demand = Demand(timeid=timeid, industryid=i+1, multiplier=d[0][i], units=pop*d[0][i])
        session.add(demand)
        session.commit()
    
    ##return a program readable demand matrix
    d = d * pop #should there be a units baseline for each industry?
    df = pd.DataFrame(d, columns=range(1,14), index=['demand']).T
    
    return df

def agg_supply(timeid):
    s_dict = {k: 0 for k in range(1, 14)}

    ##pull units devoted to production...   
    if timeid == 1 or session.query(Inventory.id).filter(Inventory.timeid==timeid-1).count() == 0:
        result = session.query(Business.industryid, func.sum(Business.produnits)).group_by(Business.industryid).order_by(Business.industryid).all()

        for id, produnits in result:
            s = produnits * 500 
            s_dict[id] = s

            ##commit supply to the database        
            supply = Supply(timeid=timeid, industryid=id, endunits=s)
            session.add(supply)
            session.commit() 
    else:
        result = session.query(Business.industryid, func.sum(Business.produnits), func.sum(Inventory.units)).filter(Inventory.timeid==timeid-1, Business.id==Inventory.businessid).group_by(Business.industryid).order_by(Business.industryid).all()

        for id, produnits, inventory in result:    
        ##calculate the supply for each record...
            s = inventory + produnits * 500 
            s_dict[id] = s
            
            ##commit supply to the database        
            supply = Supply(timeid=timeid, industryid=id, endunits=s)
            session.add(supply)
            session.commit() 
    
    ##return a supply dataframe for program    
    df = pd.DataFrame(s_dict.values(), index=s_dict.keys(), columns=["supply"])
    return df

def biz_supply(timeid, bizid):
    biz_produnits = session.query(Business.produnits).filter(Business.id==bizid).scalar()
    p = biz_produnits * 500 #units produced this round
    
    try:  
        i = session.query(Inventory.units).filter(Inventory.businessid==bizid, Inventory.timeid==timeid).scalar()
        if i == None:
            i = 0
    except NoResultFound:
        i = 0

    return {'prod':p, 'inv':i}

#def set_price(population, timeid):
    ##calculate supply and demand as of the current time...
    #d = agg_demand(population, cur_timeid)
    #s = agg_supply(cur_timeid)
    #df = pd.DataFrame([d, s], columns=["demand","supply"])    
        
    ##equate supply to demand and identify market price
    #price = pd.DataFrame(d.values / s.values, columns=["price"], index=d.index).replace(np.inf, 0)
    #return price

def get_biz_list(industry):
    ##retrieve all businesses in an industry and set the production sell through order
    biz_list = []
    for bizid in session.query(Business.id).filter(Business.industryid==int(industry)).all():
        biz_list.append(bizid[0])

    np.random.shuffle(biz_list)
    return biz_list

faker = Factory.create()

start = 29
stop = 65
    
##create one user and business to start with (using a random industry)
if session.query(Business.id).count() == 0:
    cur_timeid = 1
    rnd_industryid = random.choice(session.query(Industry.id).all())[0]
    create_biz(rnd_industryid, cur_timeid)

##core loop of simulation... 
for t in xrange(start, stop):
    ##set the current timeid for the simulation...    
    try:
        cur_timeid = session.query(Period.id).filter(Period.id==t).scalar()
    except NoResultFound:
        new_period()
        cur_timeid = session.query(Period.id).filter(Period.id==t).scalar()
    
    ##find the population as of the current time...    
    population = session.query(func.sum(Owner.population)).scalar()    
    #print population

    for id, pop in session.query(Owner.id, Owner.population).all():
        pop = pop_growth(pop)
        state = update(Owner).where(Owner.id==id).values(population=pop)
        session.execute(state)
    
    #price = set_price(population, cur_timeid)
    
    ##calculate supply and demand as of the current time...
    d = agg_demand(population, cur_timeid)
    s = agg_supply(cur_timeid)
    #df = pd.DataFrame([d, s], columns=["demand","supply"])    
    
    ##equate supply to demand and identify market price
    price = pd.DataFrame(d.values / s.values, columns=["price"], index=d.index).replace(np.inf, 0)
    
    ##identify industries that need new business based on higher demand and open those businesses
    for industry in d.index:
        gap = s.loc[industry].values - d.loc[industry].values
        if gap < 0:
            create_biz(int(industry), cur_timeid)
        
        #in cases where there is sufficient demand, run through business needs...        
        else:            
            ##identify revenue for each business
            biz_list = get_biz_list(industry)            
            
            #biz_list = []
            #for bizid in session.query(Business.id).filter(Business.industryid==int(industry)).all():
            #    biz_list.append(bizid[0])

            #np.random.shuffle(biz_list)
            
            total_demand = d.loc[industry].values[0]
            i = 0
            while total_demand > 0 and i < len(biz_list):
                try:
                    supply = biz_supply(cur_timeid, biz_list[i])
                    prod = supply['prod']
                    inv = supply['inv']
                    tot_supply = prod + inv
                ##do nothing if there are no businesses to 
                except len(biz_list) == 0:
                    break
                else:
                    ##check to ensure that there is sufficient demand to meet supply of given business
                    if total_demand - tot_supply > 0:
                        revenue = tot_supply * price.loc[industry].values[0]
                        ledger = Ledger(businessid=biz_list[i], timeid=cur_timeid, account='revenue', amount=revenue)
                        session.add(ledger)
                        session.commit()
                        
                        ##change while loop scalars...
                        total_demand = total_demand - tot_supply                    
                        i += 1
                        
                        ##clear inventory if any exists...
                        if inv > 0:
                            new_inv = update(Inventory).where(Inventory.businessid==biz_list[i], Inventory.timeid==cur_timeid).values(units=0)
                            session.execute(new_inv)
                    #where there is insufficient demand, calculate remaining revenue for current business then store the rest of the inventory
                    else:                                             
                        revenue = total_demand * price.loc[industry].values[0]
                        ledger = Ledger(businessid=biz_list[i], timeid=cur_timeid, account='revenue', amount=revenue)
                        session.add(ledger)
                        session.commit()
                        
                        inv_units = inv + (tot_supply - total_demand)
                        inventory = Inventory(businessid=biz_list[i], timeid=cur_timeid, units=inv_units, price=price.loc[industry].values[0])
                        session.add(inventory)
                        session.commit()
                        
                        ##store excess inventory
                        for n in xrange(len(biz_list) - i, len(biz_list)):
                            inventory = Inventory(businessid=biz_list[n], timeid=cur_timeid, units=tot_supply, price=price.loc[industry].values[0])
                            session.add(inventory)
                            session.commit()
                        break
    print t, population