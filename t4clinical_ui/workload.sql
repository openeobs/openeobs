select
id,
id as activity_id,
case
    when extract (epoch from  now() at time zone 'UTC' - date_scheduled)::int/60 < -46 then 10
    when extract (epoch from  now() at time zone 'UTC' - date_scheduled)::int/60 between -45 and -31 then 20
    when extract (epoch from  now() at time zone 'UTC' - date_scheduled)::int/60 between -30 and -16 then 30
    when extract (epoch from  now() at time zone 'UTC' - date_scheduled)::int/60 between -15 and 0 then 40
    when extract (epoch from  now() at time zone 'UTC' - date_scheduled)::int/60 between 1 and 15 then 50
    when extract (epoch from  now() at time zone 'UTC' - date_scheduled)::int/60 > 16 then 60
else null end as proximity_interval
from t4_clinical_activity