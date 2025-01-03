function register_component(info, t, lib_name)

   if strcmp(info.Type, 'm')
       if t == 1
           register_m_system(info, lib_name);
       elseif t == 2
           register_m_controller(info, lib_name);
       elseif t == 3
           register_m_estimator(info, lib_name);
       elseif t == 4
           register_m_disturbance_generator(info, lib_name);
       end
   elseif strcmp(info.Type, 'slx')
       if t == 1
           register_slx_component(info, 'sys', lib_name, { '__cs_slx_sys' });
       elseif t == 2
           register_slx_component(info, 'ctl', lib_name, { '__cs_slx_ctl' });
       elseif t == 3
           register_slx_component(info, 'est', lib_name, { '__cs_slx_est' });
       elseif t == 4
           register_slx_component(info, 'dist', lib_name, { '__cs_slx_dist' });
       end
   end
end
