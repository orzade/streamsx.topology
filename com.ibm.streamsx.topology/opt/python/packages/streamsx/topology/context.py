# Licensed Materials - Property of IBM
# Copyright IBM Corp. 2015

import tempfile
import os
import os.path
import json
import subprocess
import threading
import sys

#
# Submission of a python graph using the Java Application API
# The JAA is reused to have a single set of code that creates
# SPL, the toolkit, the bundle and submits it to the relevant
# environment
#

def submit(ctxtype, graph):
    """
    Submits a topology with the specified context type.
    
    Args:
        ctxtype (string): context type.  Values include:
        * DISTRIBUTED - the topology is submitted to a Streams instance.
          The bundle is submitted using `streamtool` which must be setup to submit without requiring authentication input.
        * STANDALONE - the topology is executed directly as an Streams standalone application.
          The standalone execution is spawned as a separate process
        * BUNDLE - execution of the topology produces an SPL application bundle
          (.sab file) that can be submitted to an IBM Streams instance as a distributed application.
        graph: a Topology.graph object
        
    Returns:
        None
    """    
    fj = _createFullJSON(graph)
    fn = _createJSONFile(fj)
    try:
       _submitUsingJava(ctxtype, fn)
    finally:
       # remove splpytmp json file from /tmp
       if os.path.isfile(fn):
          os.remove(fn)    
    

def _createFullJSON(graph):
    fj = {}
    fj["deploy"] = {}
    fj["graph"] = graph.generateSPLGraph()
    return fj
   

def _createJSONFile(fj) :
    tf = tempfile.NamedTemporaryFile(mode="w+t", suffix=".json", encoding="UTF-8", prefix="splpytmp", delete=False)
    tf.write(json.dumps(fj, sort_keys=True, indent=2, separators=(',', ': ')))
    tf.close()
    return tf.name

def print_process_stdout(process):
    try:
        while True:
            line = process.stdout.readline()
            if line == '' and process.poll() != None:
                break
            print(line.strip().decode("utf=8"))
    except:
        sys.err.write("Error reading from process stdout")

def print_process_stderr(process):
    try:
        while True:
            line = process.stderr.readline()
            if line == '' and process.poll() != None:
                break
            print(line.strip().decode("utf=8"))
    except:
        sys.err.write("Error reading from process stderr")


def _submitUsingJava(ctxtype, fn):
    streams_install = os.environ.get('STREAMS_INSTALL')
    if streams_install is None:
       raise "Please set the STREAMS_INSTALL system variable"

    # This is tk/opt/python/packages/streamsx/topology
    dir = os.path.dirname(os.path.abspath(__file__))
    dir = os.path.dirname(dir)
    dir = os.path.dirname(dir)
    dir = os.path.dirname(dir)
    dir = os.path.dirname(dir)
    tk_root = os.path.dirname(dir)
    jvm = os.path.join(streams_install, "java", "jre", "bin", "java")
    jaa_lib = os.path.join(tk_root, "lib", "com.ibm.streamsx.topology.jar")
    joa_lib = os.path.join(streams_install, "lib", "com.ibm.streams.operator.samples.jar")
    cp = jaa_lib + ":" + joa_lib
    args = [ jvm, "-classpath", cp,
    "com.ibm.streamsx.topology.context.StreamsContextSubmit", ctxtype, fn]
    with subprocess.Popen(args, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0) as process:
        try:
            
            stdout_thread = threading.Thread(target=print_process_stdout, args=([process]))
            stderr_thread = threading.Thread(target=print_process_stderr, args=([process]))
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            stdout_thread.start()
            stderr_thread.start()
            process.wait()
        except:
            sys.err.write("Error starting java subprocess for submission")
