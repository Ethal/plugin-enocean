#!/bin/bash

/*
 * This file is part of the NextDom software (https://github.com/NextDom or http://nextdom.github.io).
 * Copyright (c) 2018 NextDom.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, version 2.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 */

logger_write(){
    NOW=$(date +"%Y-%m-%d %T")
    echo "[$NOW][$1] : $2"
}

logger_write "INFO" "Lancement de la synchronisation des configurations"
logger_write "INFO" "Déplacement dans le répertoire de travail"
cd /tmp
logger_write "INFO" "Nettoyage du répertoire de travail"
sudo rm -rf /tmp/plugin-openenocean > /dev/null 2>&1
logger_write "INFO" "Récupération des sources (cette étape peut durer quelques minutes)"
sudo git clone --depth=1 https://github.com/nextdom/plugin-enocean.git
if [ $? -ne 0 ]; then
    logger_write "ERROR" "Unable to fetch Plugin-openenocean git. Please check your internet connexion and github access"
    exit 1
fi

BASEDIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
logger_write "INFO" "Suppression des configurations Jeedom existantes"
sudo rm -rf ${BASEDIR}/../core/config/devices/*

logger_write "INFO" "Copie des nouvelles configurations Jeedom"
cd /tmp/plugin-openenocean/core/config/devices
sudo mv * ${BASEDIR}/../core/config/devices/

logger_write "INFO" "Suppression des profils existants"
sudo rm -rf ${BASEDIR}/../resources/openenoceand/enocean/eep/*

logger_write "INFO" "Copie des nouveaux profils"
cd /tmp/plugin-openenocean/resources/openenoceand/enocean/eep
sudo mv * ${BASEDIR}/../resources/openenoceand/enocean/eep/

logger_write "INFO" "Nettoyage du répertoire de travail"
sudo rm -R /tmp/plugin-openenocean
sudo chown -R www-data:www-data ${BASEDIR}/../resources/openenoceand/enocean/eep/
sudo chown -R www-data:www-data ${BASEDIR}/../core/config/devices/

logger_write "INFO" "Vos configurations sont maintenant à jour !"
