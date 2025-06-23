classdef ComponentRegister


    methods (Static)
        function cls = get(comp)
            if is_component_type(comp, 'mat')
                cls = MatComponentRegister;
            elseif is_component_type(comp, 'slx')
                cls = SlxComponentRegister;
            elseif is_component_type(comp, 'py')
                cls = PyComponentRegister;
            else
                error('Unknown component register');
            end
        end

        function ext = get_supported_plugin_types()
            ext = ["mat", "slx", "py"];
        end

        function ext = get_supported_plugin_file_extensions()
            ext = [".m", ".slx", ".py"];
        end

        function typ = get_plugin_type_from_file(component_path)
            splits = split(component_path, ':');
            component_path = splits{1};
        
            [~, ~, ext] = fileparts(component_path);
                
            if strcmp(ext, '.m')
                typ = "mat";
            elseif strcmp(ext, '.slx')
                typ = "slx";
            elseif strcmp(ext, '.py')
                typ = "py";
            else
                error("Error identifying plugin from file. Unknown plugin type.")
            end
        end

        function unregister(name, lib_name)
            info = get_plugin_info_from_lib(name, lib_name);
            if info.T == 1
                 ComponentRegister.unregister_system_(name, lib_name);
            elseif info.T == 2
                ComponentRegister.unregister_controller_(name, lib_name);
            elseif info.T == 3
                ComponentRegister.unregister_estimator_(name, lib_name);
            elseif info.T == 4
                ComponentRegister.unregister_disturbance_generator_(name, lib_name);
            end
        end

        function unregister_system_(name, lib_name)
            ComponentRegister.unregister_component_(name, lib_name, 'sys');
        end

        function unregister_controller_(name, lib_name)
            ComponentRegister.unregister_component_(name, lib_name, 'ctl');
        end


        function unregister_estimator_(name, lib_name)
            ComponentRegister.unregister_component_(name, lib_name, 'est');
        end


        function unregister_disturbance_generator_(name, lib_name)
            ComponentRegister.unregister_component_(name, lib_name, 'dist');
        end

        function unregister_component_(name, lib_name, typ)
            n = strcat(lib_name, '_', typ);
            block_path = fullfile(n, name);
            load_and_unlock_system(n);
            try
                delete_block(block_path);
                save_system(n);
            catch
            end
            close_system(n);
        end

    end
end