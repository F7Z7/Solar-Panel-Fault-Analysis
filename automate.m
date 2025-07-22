model='base_model_solar';
load_system(model)


irradiance_value = 100:100:1000; % irradiance value from  0 to 1000
temp_values = 2:2:50;


results=[];

for T=temp_values
    for Ir=irradiance_value

        %set simulink params using matlab
        set_param([model '/Ir'], 'Value', num2str(Ir));
        set_param([model '/T'], 'Value', num2str(T));

try
      simOut = sim(model, ...
    'Solver', 'ode23tb', ...            % Stiff solver
    'MaxStep', '1e-4', ...
    'RelTol', '1e-3', ...
    'AbsTol', '1e-4');

out = evalin('base', 'simOut');
V_PV = out.V_PV(end);
I_PV = out.I_PV(end);

        results=[results;Ir T V_PV I_PV];
        catch ME
            warning("Simulation failed at Ir=%.1f, T=%.1f — skipping", Ir, T);
            results = [results; Ir, T, NaN, NaN];  % fill with NaN
        end
    end
end


resultTable = array2table(results, 'VariableNames', {'Irradiance', 'Temperature', 'V_PV', 'I_PV'});
writetable(resultTable, 'solar_sim_results.csv');
