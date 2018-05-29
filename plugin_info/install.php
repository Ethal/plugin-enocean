<?php

/* This file is part of Jeedom.
 *
 * Jeedom is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Jeedom is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Jeedom. If not, see <http://www.gnu.org/licenses/>.
 */

/* Update by Ethal
  Last Updated: MAY 29 2018.
 */


require_once dirname(__FILE__) . '/../../../core/php/core.inc.php';

function openenocean_install() {
	if (config::byKey('api::openenocean::mode') == '') {
		config::save('api::openenocean::mode', 'localhost');
	}
}

function openenocean_update() {
	if (config::byKey('api::openenocean::mode') == '') {
		config::save('api::openenocean::mode', 'localhost');
	}
}

function openenocean_remove() {

}

?>
