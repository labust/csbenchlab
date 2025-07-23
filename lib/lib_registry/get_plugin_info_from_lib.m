function p = get_plugin_info_from_lib(name, lib_name)
    lib_path = get_component_library(lib_name).Path;
   
    try
        manifest = load(fullfile(lib_path, 'autogen', 'manifest.mat'));
        registry = manifest.registry;
    catch
        error(strcat("Manifest file not found for library '",  n.name));
    end
    
    fns = fieldnames(registry);
    for i=1:length(fns)
        v = registry.(fns{i});
        for j=1:length(v)
            if strcmp(v{j}.Name, name)
                p = v{j};
                return
            end
        end
    end
    p = [];
end
    



