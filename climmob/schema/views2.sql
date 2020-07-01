SELECT * FROM (( 
SELECT pkgcomb.package_id,package.package_code, 
technology.tech_name,techalias.alias_name,pkgcomb.comb_order FROM 
pkgcomb,package,prjcombination,prjcombdet,prjalias,techalias, 
technology WHERE 
pkgcomb.user_name = package.user_name AND 
pkgcomb.project_cod = package.project_cod AND 
pkgcomb.package_id = package.package_id AND 
pkgcomb.comb_user = prjcombination.user_name AND 
pkgcomb.comb_project = prjcombination.project_cod AND 
pkgcomb.comb_code = prjcombination.comb_code AND 
prjcombination.user_name = prjcombdet.prjcomb_user AND 
prjcombination.project_cod = prjcombdet.prjcomb_project AND 
prjcombination.comb_code = prjcombdet.comb_code AND 
prjcombdet.user_name = prjalias.user_name AND 
prjcombdet.project_cod = prjalias.project_cod AND 
prjcombdet.tech_id = prjalias.tech_id AND 
prjcombdet.alias_id = prjalias.alias_id AND 
prjalias.tech_used = techalias.tech_id AND 
prjalias.alias_used = techalias.alias_id AND 
techalias.tech_id = technology.tech_id AND 
prjalias.tech_used IS NOT NULL AND 
pkgcomb.user_name = 'qlands' AND 
pkgcomb.project_cod = 'prj005'
ORDER BY pkgcomb.package_id,pkgcomb.comb_order) 
UNION 
(SELECT pkgcomb.package_id,package.package_code, 
technology.tech_name,prjalias.alias_name,pkgcomb.comb_order FROM 
pkgcomb,package,prjcombination,prjcombdet,prjalias, 
technology WHERE 
pkgcomb.user_name = package.user_name AND 
pkgcomb.project_cod = package.project_cod AND 
pkgcomb.package_id = package.package_id AND 
pkgcomb.comb_user = prjcombination.user_name AND 
pkgcomb.comb_project = prjcombination.project_cod AND 
pkgcomb.comb_code = prjcombination.comb_code AND 
prjcombination.user_name = prjcombdet.prjcomb_user AND 
prjcombination.project_cod = prjcombdet.prjcomb_project AND 
prjcombination.comb_code = prjcombdet.comb_code AND 
prjcombdet.user_name = prjalias.user_name AND 
prjcombdet.project_cod = prjalias.project_cod AND 
prjcombdet.tech_id = prjalias.tech_id AND 
prjcombdet.alias_id = prjalias.alias_id AND 
prjcombdet.tech_id = technology.tech_id AND 
prjalias.tech_used IS NULL AND 
pkgcomb.user_name = 'qlands' AND 
pkgcomb.project_cod = 'prj005'
ORDER BY pkgcomb.package_id,pkgcomb.comb_order)) AS T ORDER BY T.package_id,T.comb_order,T.tech_name;

