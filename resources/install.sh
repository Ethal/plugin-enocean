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

touch /tmp/dependancy_openenocean_in_progress
echo 0 > /tmp/dependancy_openenocean_in_progress
echo "********************************************************"
echo "*             Installation des dépendances             *"
echo "********************************************************"
apt-get update
echo 50 > /tmp/dependancy_openenocean_in_progress
apt-get remove -y python-enum
echo 60 > /tmp/dependancy_openenocean_in_progress
apt-get install -y  python-requests python-serial python-pyudev 
echo 75 > /tmp/dependancy_openenocean_in_progress
pip install enum-compat
echo 85 > /tmp/dependancy_openenocean_in_progress
pip install beautifulsoup4
echo 100 > /tmp/dependancy_openenocean_in_progress
echo "********************************************************"
echo "*             Installation terminée                    *"
echo "********************************************************"
rm /tmp/dependancy_openenocean_in_progress
