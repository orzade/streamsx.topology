package com.ibm.streamsx.topology.test.api;

import static com.ibm.streamsx.topology.test.TestTopology.SC_OK;
import static org.junit.Assume.assumeTrue;

import java.math.BigInteger;

import org.junit.Test;

import com.ibm.streamsx.topology.TStream;
import com.ibm.streamsx.topology.Topology;
import com.ibm.streamsx.topology.context.StreamsContext;
import com.ibm.streamsx.topology.context.StreamsContextFactory;
import com.ibm.streamsx.topology.function7.Function;

import com.ibm.streams.operator.PERuntime;
import com.ibm.streams.operator.Tuple;

public class LowLatencyTest {
    @Test
    public void simpleLowLatencyTest() throws Exception{
        assumeTrue(SC_OK);
        Topology topology = new Topology("lowLatencyTest");

        // Construct topology
        TStream<String> ss = topology.strings("hello");
        TStream<String> ss1 = ss.transform(getPEId(), String.class).lowLatency();
        TStream<String> ss2 = ss1.transform(getPEId(), String.class).endLowLatency();
        ss2.print();
        
        StreamsContextFactory.getStreamsContext(StreamsContext.Type.TOOLKIT).submit(topology).get();
    }
    
    @Test
    public void multipleRegionLowLatencyTest() throws Exception{
        assumeTrue(SC_OK);
        Topology topology = new Topology("lowLatencyTest");

        // Construct topology
        TStream<String> ss = topology.strings("hello")
                .transform(getPEId(), String.class).transform(getPEId(), String.class);
        
        TStream<String> ss1 = ss.transform(getPEId(), String.class).lowLatency();
        TStream<String> ss2 = ss1.transform(getPEId(), String.class).
                transform(getPEId(), String.class).endLowLatency().transform(getPEId(), String.class);
        TStream<String> ss3 = ss2.transform(getPEId(), String.class).lowLatency();
        ss3.transform(getPEId(), String.class).transform(getPEId(), String.class)
            .endLowLatency().print();
        
        StreamsContextFactory.getStreamsContext(StreamsContext.Type.TOOLKIT).submit(topology).get();
    }
    
    @SuppressWarnings("serial")
    private static Function<String, String> getPEId(){
        return new Function<String, String>(){
            int counter = 0;
            @Override
                public String apply(String v) {
                // TODO Auto-generated method stub
                return ((BigInteger) PERuntime.getCurrentContext().getPE().getPEId()).toString();
            }

        };
    }
}
