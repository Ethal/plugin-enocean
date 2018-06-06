<?php

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

/* Update by Ethal
  Last Updated: MAY 29 2018.
 */


require_once dirname(__FILE__) . '/../../../../core/php/core.inc.php';

global $jsonrpc;
if (!is_object($jsonrpc)) {
	throw new Exception(__('JSONRPC object not defined', __FILE__), -32699);
}

if ($jsonrpc->getMethod() == 'deamonStart') {
	log::add('openenocean', 'debug', 'Envoi des ids à tous les demons');
	openenocean::sendIdToDeamon();
	$jsonrpc->makeSuccess('ok');
}

$params = $jsonrpc->getParams();

throw new Exception(__('Aucune methode correspondante pour le plugin Enocean : ' . $jsonrpc->getMethod(), __FILE__));
?>
