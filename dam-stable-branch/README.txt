Web Server
==========
 * HD     - 2Gb
 * Memory - 256Mb

Worker
======
 * HD     - 4Gb
 * Memory - 256Mb

Storage
=======
 * HD     - xxx Gb
 * NFS



Network
=======
 * /etc/networking/interfaces
--------
iface eth1 inet static
   address 192.168.0.1
   netmask 255.255.255.0
--------

 * Forward the SSH port of NATed server:
--------
MACHINE="DAM - Web Server"
VBoxManage setextradata "$MACHINE" "VBoxInternal/Devices/e1000/0/LUN#0/Config/ssh/HostPort" 2001
VBoxManage setextradata "$MACHINE" "VBoxInternal/Devices/e1000/0/LUN#0/Config/ssh/GuestPort" 22
VBoxManage setextradata "$MACHINE" "VBoxInternal/Devices/e1000/0/LUN#0/Config/ssh/Protocol" TCP
--------

 * Extra packages:
   cat /etc/apt/sources.list | sed 's/gb\./es\./g' > /tmp/a && cp /tmp/a /etc/apt/sources.list
   sudo apt-get install emacs22-nox openssh-server

 * Emacs
   scp -P 2001 -r .emacs.d localhost:



Launch Virtual Servers
======================
VBoxHeadless -s "DAM - Web Server"


More info
=========

Makefile targets
----------------
make dbslayer - Launches a Cherokee DB load balancer on TCP port 33060
make web      - Launches a Cherokee Web Server on TCP port 9091
make worker   - Launches a Queue worker
make update   - Update the source code tree
make queue    - Launches the Queue load balancer

Directory Layout
----------------
src/          - Python source code
database/     - EER Model for MySQL Workbench 5.2.11
frontend/     - HTTP Load Balancer
qa/           - Quality Assurance tests

Full Search queries are a very nice feature to have, but that means
you must use a MyISAM engine for your MySQL database. Since it has no
transaction support, a MyISAM table called fullsearch is used just for
this. A FULLTEXT index is needed:


Architecture layout
-------------------

                  -->  Back-end 1  -----
                 |     [Port 9091]      |
                 |                      |                    -> MySQL 1
Front-end -------|-->  Back-end 2  -----|-->   DBSlayer  ---|
[Port 80]        |     [Server2: 9091]  |    [Port 33060]    -> MySQL 2
                 |                      |
                  -->  Back-end 3  -----
                       [Server3: 9091]


                  -->  Transcode-engine 1
                 |     [Port 8003]
                 |
Queue-balancer --|-->  Transcode-engine 2
[Port 8001]      |     [Port 8003]
                 |
                  -->  Transcode-engine 3
                       [Port 8003]


FULLTEXT Restrictions
---------------------

Activae has two search modes: free text searches (FULLTEXT) and
seaches by database field.

A few restrictions affect MySQL FULLTEXT indices. Some of the default
behaviors of these restrictions can be changed in your my.cnf or using
the SET command.

    * By default, if a search term appears in more than 50% of the
      rows then MySQL will not return any results.
    * By default, your search query must be at least four characters
      long and may not exceed 254 characters.
    * MySQL has a default stopwords file that has a list of common
      words (i.e., the, that, has) which are not returned in your
      search. In other words, searching for them will return zero rows.
    * MySQL requires that you have at least three rows of data in your
      result set before it will return any results.
    * FULLTEXT indices are NOT supported in InnoDB tables.
    * According to MySQL's manual, the argument to AGAINST() must be a
      constant string. In other words, you cannot search for values
      returned within the query.

