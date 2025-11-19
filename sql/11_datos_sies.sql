select periodo,
       codcli,
       codplan,
       sies_completo,
       anio_ing_act,
       sem_ing_act,
       anio_ing_ori,
       sem_ing_ori
from [DWH_DAI_Server].DWH_DAI.dbo.ft_sies
where periodo >= 2022
order by periodo asc