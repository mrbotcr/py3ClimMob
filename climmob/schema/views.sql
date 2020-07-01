SELECT * FROM (
(SELECT prjcombdet.comb_code,prjcombination.comb_usable,prjcombdet.tech_id,techalias.alias_id,techalias.alias_name,prjcombdet.alias_order FROM 
prjcombdet,prjalias,techalias,prjcombination WHERE 
prjcombdet.user_name = prjalias.user_name AND 
prjcombdet.project_cod = prjalias.project_cod AND 
prjcombdet.tech_id = prjalias.tech_id AND 
prjcombdet.alias_id = prjalias.alias_id AND 
prjalias.tech_used = techalias.tech_id AND 
prjalias.alias_used = techalias.alias_id AND 
prjcombdet.prjcomb_user = prjcombination.user_name AND 
prjcombdet.prjcomb_project = prjcombination.project_cod AND 
prjcombdet.comb_code = prjcombination.comb_code AND 
prjcombdet.prjcomb_user = 'qlands' AND 
prjcombdet.prjcomb_project = 'prj005' AND
prjalias.tech_used IS NOT NULL 
ORDER BY prjcombdet.comb_code,prjcombdet.alias_order) 
UNION 
(SELECT prjcombdet.comb_code,prjcombination.comb_usable,prjcombdet.tech_id,concat('C',prjalias.alias_id) as alias_id,prjalias.alias_name,alias_order FROM 
prjcombdet,prjalias,prjcombination WHERE 
prjcombdet.user_name = prjalias.user_name AND 
prjcombdet.project_cod = prjalias.project_cod AND 
prjcombdet.tech_id = prjalias.tech_id AND 
prjcombdet.alias_id = prjalias.alias_id AND 
prjcombdet.prjcomb_user = prjcombination.user_name AND 
prjcombdet.prjcomb_project = prjcombination.project_cod AND 
prjcombdet.comb_code = prjcombination.comb_code AND 
prjcombdet.prjcomb_user = 'qlands' AND 
prjcombdet.prjcomb_project = 'prj005' AND
prjalias.tech_used IS NULL 
ORDER BY prjcombdet.comb_code,prjcombdet.alias_order)) as T ORDER BY T.comb_code,T.alias_order;