function unregister_controller(name, lib_name)
    
    block_path = strcat(lib_name, '_ctl', '/', name);
    delete_block(block_path);
    

end