function mux = get_controller_mux_struct(path)
    pa = @BlockHelpers.path_append;
    mux.Input = [];
    mux.Output = [];

    parent_path = get_parent_controller(path);
    
    splits = split(parent_path, '/');
    demux_path = pa(splits{1:end-1}, 'DemuxYrefIn');
    mux_path = pa(splits{1:end-1}, 'MuxOut');


    demux_port = get_param(demux_path, 'PortHandles');
    mux_port = get_param(mux_path, 'PortHandles');

    for i=1:length(demux_port.Outport)
        line = get_param(demux_port.Outport(i), 'Line');
        if line == -1 
            continue
        end
        srcport = get_param(line, 'Dstporthandle');      
        if srcport == -1
            continue
        end
        mux.Input = [mux.Input, i];
    end
        
    for i=1:length(mux_port.Inport)
        line = get_param(mux_port.Inport(i), 'Line');
        if line == -1 
            continue
        end
        srcport = get_param(line, 'Srcporthandle');      
        if srcport == -1
            continue
        end
        mux.Output = [mux.Output, i];
    end
end
