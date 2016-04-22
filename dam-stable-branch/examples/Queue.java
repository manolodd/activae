// Compile:
//   javac -classpath xmlrpc-1.1.jar -Xlint:unchecked Queue.java
// Execute:
//   java -classpath .:./xmlrpc-1.1.jar Queue

import org.apache.xmlrpc.XmlRpcClient;
import java.util.Vector;

public class Queue {
 public static void main (String [] args) {
  try {
     XmlRpcClient client = new XmlRpcClient("http://217.116.6.26:8001/");

     Vector params = new Vector();
     params.addElement (new String("/tmp/test.png"));
     params.addElement (new String("/tmp/target.jpg"));
     params.addElement (new String("jpg"));

     Object result = client.execute("ConvertImage", params);

     int task_id = ((Integer) result).intValue();
     System.out.println("ConvertImage(): Task ID is "+ task_id);


     params = new Vector();
     params.addElement(new String("/tmp/test.png"));
     result = client.execute("GetInfoImage", params);
     // Possible returns: "failed" |  ("ok", dict_info)
     System.out.println("GetInfoImage(): "+ result);

     params = new Vector();
     params.addElement(new Integer(task_id));
     result = client.execute("GetTaskStatus", params);
     System.out.println("GetTaskStatus(): "+ result);

   } catch (Exception exception) {
     System.err.println("Queue: " + exception);
   }
  }
}
