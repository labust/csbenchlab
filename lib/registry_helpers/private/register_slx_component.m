function register_slx_component(info, typ, lib_name, tags)
    load_system(info.model_name);
    src = fullfile(info.model_name, info.rel_path);
    splits = split(info.rel_path, '/');
    name = splits{end};
    dest = strcat(lib_name, '_', typ);

   

    load_and_unlock_system(dest);
    try
        add_block(src, fullfile(dest, name));

         for i=1:length(tags)
            model_append_tag(fullfile(dest, name), tags{i});
        end

        save_system(dest);
    catch
    end
    close_system(info.model_name, 0);
    close_system(dest);
end

    