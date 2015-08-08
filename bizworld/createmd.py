# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import random
from faker import Factory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models

##Fake data maker
faker = Factory.create()

##SQL Alchemy engine and session makers    
engine = create_engine("postgresql+psycopg2://Josh:@localhost/bizworld")
Session = sessionmaker(bind=engine)
session = Session()

##used for adding industries from scratch
def add_industries():
    path = "c:\users\josh\documents\\bizworld"
    industries = pd.read_csv(path + "\\bizworld-industries.csv", index_col=0)
    
    for i in range(len(industries)):
        industry = models.Industry(id=i+1, alias=industries.values[i][0])
        session.add(industry)
    
    session.commit()
    return "done"    

def create_owner(starttimeid):
    fn = faker.first_name()
    ln = faker.last_name()
    alias = fn + ' ' + ln    
    email = fn + '.' + ln + '@' + faker.free_email_domain()
    
    owner = models.Owner(alias=alias, email=email, starttimeid=starttimeid)
    session.add(owner)
    session.commit()
    
    return owner

def create_biz(industryid, starttimeid):
    alias = faker.company()
    owner_expand = np.random.randint(1,100)
    
    if owner_expand < 10:
        try:        
            ownerid = random.sample(session.query(models.Owner.id).all(), 1)[0][0]
        except ValueError:
            create_owner(starttimeid)
            ownerid = session.query(models.Owner.id).order_by("Owner.id DESC").limit(1).scalar()
    else:
        create_owner(starttimeid)
        ownerid = session.query(models.Owner.id).order_by("Owner.id DESC").limit(1).scalar()
    
    biz = models.Business(alias=alias, ownerid=ownerid, produnits=1, industryid=industryid, starttimeid=starttimeid)
    session.add(biz)
    session.commit()
    
    return biz

##used to update periods
def new_period():
    prior = session.query(models.Period).order_by("Period.id DESC").limit(1).first()
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

    period = models.Period(simyear=simyear, simmonth=simmonth, simweek=simweek, simday=simday)
    session.add(period)
    session.commit()        
    return new