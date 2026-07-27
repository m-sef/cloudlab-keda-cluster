"""Variable number of nodes in a lan. You have the option of picking from one
of several standard images we provide, or just use the default (typically a recent
version of Ubuntu). You may also optionally pick the specific hardware type for
all the nodes in the lan. 

Instructions:
Wait for the experiment to start, and then log into one or more of the nodes
by clicking on them in the toplogy, and choosing the `shell` menu option.
Use `sudo` to run root commands. 
"""

# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as protogeni
# Emulab specific extensions.
import geni.rspec.emulab as emulab

# Create a portal context, needed to defined parameters
portal_context = portal.Context()

# Create a Request object to start building the RSpec.
request = portal_context.makeRequestRSpec()

# Variable number of nodes.
portal_context.defineParameter(
    "workerNodeCount", "Number of Worker Nodes",
    portal.ParameterType.INTEGER, 1,
    longDescription="The number of worker nodes, in addition to the client node")

# Pick your OS.
imageList = [
    ('default', 'Default Image'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU24-64-STD', 'Ubuntu 24.04'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-STD', 'Ubuntu 22.04'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD', 'Ubuntu 20.04'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU18-64-STD', 'Ubuntu 18.04'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//CENTOS9S-64-STD', 'CentOS 9 Stream'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//CENTOS8S-64-STD', 'CentOS 8 Stream'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//ROCKY9-64-STD',   'Rocky Linux 9'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//FBSD135-64-STD',  'FreeBSD 13.5'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//FBSD142-64-STD',  'FreeBSD 14.2')
]

portal_context.defineParameter(
    "osImage", "Select OS image",
    portal.ParameterType.IMAGE, imageList[0], imageList,
    longDescription="Most clusters have this set of images, pick your favorite one.")

# Optional physical type for all nodes.
portal_context.defineParameter(
    "workerPhystype", "Worker physical node type",
    portal.ParameterType.NODETYPE, "",
    longDescription="Pick a single physical node type (pc3000,d710,etc) instead of letting the resource mapper choose for you.")

portal_context.defineParameter(
    "masterPhystype", "Master physical node type",
    portal.ParameterType.NODETYPE, "",
    longDescription="Pick a single physical node type (pc3000,d710,etc) instead of letting the resource mapper choose for you.")

# Optional link speed, normally the resource mapper will choose for you based on node availability
portal_context.defineParameter(
    "linkSpeed", "Link Speed",
    portal.ParameterType.INTEGER, 0,
    [
        (0,        "Any"),
        (100000,   "100Mb/s"),
        (1000000,  "1Gb/s"),
        (10000000, "10Gb/s"),
        (25000000, "25Gb/s"),
        (100000000,"100Gb/s")
    ],
    advanced=True,
    longDescription="""A specific link speed to use for your lan.
                       Normally the resource mapper will choose for you based on node availability and the optional physical type.""")
                    
# Sometimes you want all of nodes on the same switch, Note that this option can make it impossible
# for your experiment to map.
portal_context.defineParameter(
    "sameSwitch", "No Interswitch Links",
    portal.ParameterType.BOOLEAN, False,
    advanced=True,
    longDescription="""Sometimes you want all the nodes connected to the same switch. 
                       This option will ask the resource mapper to do that, although it might make
                       it imppossible to find a solution. Do not use this unless you are sure you need it!""")

# Retrieve the values the user specifies during instantiation.
parameters = portal_context.bindParameters()

# Check parameter validity.
if parameters.workerNodeCount < 1:
    portal_context.reportError(portal.ParameterError("You must choose at least 1 worker node.", ["workerNodeCount"]))

portal_context.verifyParameters()

local_area_network = request.LAN()

if parameters.linkSpeed > 0:
    local_area_network.bandwidth = parameters.linkSpeed
    
if parameters.sameSwitch:
    local_area_network.setNoInterSwitchLinks()

# Process worker nodes, adding to link or lan.
for i in range(parameters.workerNodeCount):
    # Create a node and add it to the request
    worker_node_name = "worker" + str(i)
    worker_node = request.RawPC(worker_node_name)
    worker_node.addService(protogeni.Execute(shell="sh", command="/local/repository/scripts/setup.sh"))

    if parameters.osImage and parameters.osImage != "default":
        worker_node.disk_image = parameters.osImage
    
    # Add node to LAN
    worker_node_interface = worker_node.addInterface("eth1")
    local_area_network.addInterface(worker_node_interface)
  
    # Optional hardware type.
    if parameters.workerPhystype != "":
        worker_node.hardware_type = parameters.workerPhystype

# Create master node
master_node = request.RawPC("master")

if parameters.masterPhystype != "":
    master_node.hardware_type = parameters.masterPhystype

if parameters.osImage and parameters.osImage != "default":
    master_node.disk_image = parameters.osImage

master_node.addService(protogeni.Execute(shell="sh", command="/local/repository/scripts/setup.sh"))
master_node_interface = master_node.addInterface("eth1")
local_area_network.addInterface(master_node_interface)

# Print the RSpec to the enclosing page.
portal_context.printRequestRSpec(request)