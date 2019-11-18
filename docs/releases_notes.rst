Releases notes
---------------


dev
====

* Mettre à jour la fonction driver_help() depuis qu’il n’y a plus de ..._by_config
* Mettre à jour le notebook jupyter dans le drive depuis qu’il n’y a plus de _by_config
* Fonction autolab.explore_driver() qui liste toutes les classes et toutes les fonctions de chaque classe (prend une instance de classe en argument)
* Fonction autolab.infos() qui liste les paths des drivers, la liste de drivers dans chaque path, et la liste des devices préconfigurés ready to us (see: autolab driver -h)
* Fonction get_method_args() qui liste toutes les méthodes d’une instance
* Renommer fonctions [...]_driver_config en [...]_local_config, y compris dans la doc
* Renommer tous les driver_parser en driver_utilities
* Transférer la catégorie du driver.py au driver_utilities
* Supprimer autolab.show_drivers() et afficher les catégories dans autolab.infos()
* Renommer autolab.help() en autolab.doc() et ‘autolab documentation’ en ‘autolab doc’


Documentation 
[DONEish] make your own driver, test it in the local folder, then send it to us by mail
os shell
[DONE] mentionner le fait que l’on peut overwriter les paramètres d’une local config
[DONE] logos (c2n, cnrs, hypnotic, UNIFY)
copyright (?)
releases notes page ?
	Fusion parsers dans autolab_new.py
[HALF DONE] fusion des parsers pour l’instantiation des devices et drivers
[DONE] Supprimer le fichier driver_parser_utilities ultra redondant avec drivers.py, sauf la derniere fonction a mettre dans autolab new (plus besoin use exec only)
[DONE] virer dans les commandes processed I., virer partial define -m channel1.amplitude(2,b=’test’), put -m in autolab_driver.py (and not in do_something)
faire la même chose dans autolab device
“””autolab-drivers -D nickname -m some_methods1,arg1,arg2=23 some_methods2,arg1='test'
Execute some_methods of the driver. A list of available methods is present at the top of this help along with arguments definition.”””  in autolab_driver and pass in arguments
[DONE] (OS) autolab infos: appel de la fonction autolab.infos()
Virer les imports dans les driver_utilities.py
Supprimer autolab.py, autolab_device.py, autolab_driver.py et renommer autolab_new.py en autolab.py
[DONE] modify config.help(from_parser=True), keep same structure. Just need to fill for parser approach
[DONE] PRINT = True to return string of help functions WITH OPTION _print

Core:



Drivers:

 * exfo_PM1613: fixed problem for 
 * yokogawa_...


v1.0
=====

* First push
