SELECT 
  inventory.timeid, 
  business.industryid, 
  sum(inventory.units) as "inventory"
FROM 
  public.inventory, 
  public.business
WHERE 
  business.id = inventory.businessid
GROUP BY
  inventory.timeid,
  business.industryid
ORDER BY
  inventory.timeid,
  business.industryid
