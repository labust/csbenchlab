function unregister_disturbance_generator(name, lib_name)
    n = strcat(lib_name, '_dist');
    block_path = fullfile(n, name);
    load_and_unlock_system(n);
    try
        delete_block(block_path);
        save_system(n);
    catch
    end
    close_system(n);
end
