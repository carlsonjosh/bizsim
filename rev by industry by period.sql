select 
	l.timeid as "timeid", 
	b.industryid as "industry", 
	count(b.id) as "biz cnt", 
	sum(l.amount) as "revenue"
from 
	business as b inner join ledger as l on b.id=l.businessid
where l.account like 'revenue'
group by l.timeid, b.industryid
order by l.timeid, b.industryid