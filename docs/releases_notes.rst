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

v1.0
=====

* First push
