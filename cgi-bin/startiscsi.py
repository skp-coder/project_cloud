#!/usr/bin/python2


import cgi
import commands


print 'content-type:text/html'

print ''

import mysql.connector as mariadb


db=mariadb.connect(user='root',password='redhat',database='welkins')

cursor=db.cursor()

print '''

<!DOCTYPE html>
<html>
<head>
<style>
.but{
	background:blue;
	color:white;
	text-align:center;
	text-decoration:none;
	border-radius:4px;
	border:2px groove blue;
	padding:4px;
}
</style>
</head>
<body>

<div>
<h2 style="color:grey;">Eureka:</h2>
<form method="post">
<b>ISCSI mode:</b><br /><br />
<table>
<tr>
<td><b>Enter size of block storage:</b></td>
<td><input type="number" name="size" value=""/> </td></tr>
<tr>
<td><b>Enter name of storage folder:</b></td>
<td><input type="text" name="obj_n" value=""/></td></tr>

<br />
<tr>
<td><input class="but" type="submit" value="Launch"/></td></tr>
</table>
</form>
</div>
</body>
</html>
'''

user=commands.getstatusoutput('cat /var/www/html/user_log')

conf=cgi.FormContent()
size=conf['size'][0]
name=conf['obj_n'][0]
commands.getstatusoutput('sudo lvcreate --size {}G --name {} /dev/cloud'.format(size,name))
commands.getstatusoutput('sudo touch /etc/tgt/conf.d/{}.conf'.format(name))
commands.getstatusoutput('sudo chmod o+w /etc/tgt/conf.d/{}.conf'.format(name))
y=open('/etc/tgt/conf.d/{}.conf'.format(name),mode='w')
y.write('<target '+name+'>\n')
y.write('\t\tbacking store /dev/cloud/'+name+'\n')
y.write('</target>\n')
y.close()
commands.getstatusoutput('sudo systemctl restart tgtd')

commands.getstatusoutput('sudo sleep 5')

commands.getstatusoutput('sudo touch /{}.sh'.format(name))
commands.getstatusoutput('sudo chmod 777 /{}.sh'.format(name))
x=open('/{}.sh'.format(name),mode='w')
x.write('#!/usr/bin/bash\n\n')
x.write('yum install iscsi-initiator-utils -y\n')
x.write('iscsiadm --mode discoverydb --type sendtargets --portal www.welkins.com --discover\n')
x.write('iscsiadm --mode node --targetname '+name+' --portal www.welkins.com:3260 --login\n')
x.write('read a\n')
x.close()
commands.getstatusoutput('sudo tar -cvf /{0}.tar /{0}.sh'.format(name))
commands.getstatusoutput('sudo mv /{}.tar /var/www/html/'.format(name))

cursor.execute("INSERT into blk VALUES (%s,%s,'active')",(user[1],name))

db.commit()

db.close()

print "Successfull!!!"
print "<META HTTP-EQUIV=refresh CONTENT=\"0;URL=http://www.welkins.com/{}.tar\">\n".format(name)

