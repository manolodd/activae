<?php
include("xmlrpc.inc");

// Make an object to represent our server.
$server   = new xmlrpc_client("http://217.116.6.26:8002/");

// Info
$message = new xmlrpcmsg('info');
$result  = $server->send($message);
$struct  = $result->value();
$name    = $struct->structmem('name')->scalarval();
$version = $struct->structmem('version')->scalarval();
print "Info: $name, $version\n";

// Ping
$message = new xmlrpcmsg('ping');
$result  = $server->send($message);
$struct  = $result->value();
print "Ping: OK\n";

// Search
$query = array(new xmlrpcval(
                   array("creator_id" => new xmlrpcval(1, "int")),
                   "struct"));
$message = new xmlrpcmsg('search', $query);
$result  = $server->send($message);
$val     = php_xmlrpc_decode ($result->value());
$str     = "";
while (list($k,$v) = each($val)) {
      $str = $str . "$v ";
}
print "Search: $str\n";

// GET
$id      = $val[0];
$message = new xmlrpcmsg('get', array (new xmlrpcval($id, "int")));

$result  = $server->send($message);
print "Get: $id\n";
print $result->serialize();
?>
