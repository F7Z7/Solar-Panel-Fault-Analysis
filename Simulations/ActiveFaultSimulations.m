clear; clc;

% List of fault models (Simulink .slx or .mdl files)
model_Arr = ["short_circuit.slx", "open_circuit.slx", "line_to_ground.slx", "line_to_line.slx"];
fault_names = ["ShortCircuit", "OpenCircuit", "LineToGround", "LineToLine"];

% Define range of irradiance and temperature
irradiance_values = 100:100:1000;   % W/m^2
temperature_values = 15:10:45;      % °C

for i = 1:length(model_Arr)
    
    model = model_Arr(i);
    fault_name = fault_names(i);
    
    load_system(model);   % Load the model
    
    results = [];         % Initialize storage for this fault
    
    for Ir = irradiance_values
        for T = temperature_values
            
            % Assign to workspace
            assignin("base", "Ir", Ir);
            assignin("base", "T", T);
            
            try
                % Run simulation
                simOut = sim(model, ...
                    'StartTime', '0', ...
                    'StopTime', '0.5', ...
                    'Solver', 'ode23tb', ...
                    'MaxStep', 1e-6, ...
                    'RelTol', 1e-3, ...
                    'AbsTol', 1e-4);
                
                % Extract outputs
                V_PV = NaN; I_PV = NaN;
                
                V_data = simOut.get("V_PV");
                I_data = simOut.get("I_PV");
                
                if isnumeric(V_data) && ~isempty(V_data)
                    V_PV = V_data(end);
                end
                if isnumeric(I_data) && ~isempty(I_data)
                    I_PV = I_data(end);
                end
                
                P_PV = V_PV * I_PV;
                
                % Append to results
                results = [results; Ir, T, V_PV, I_PV, P_PV];
                
                fprintf('Fault: %s | Ir=%4.0f T=%2.0f → V=%.2f I=%.2f\n', fault_name, Ir, T, V_PV, I_PV);
                
            catch ME
                fprintf('Simulation failed for %s at Ir=%4.0f T=%2.0f — %s\n', fault_name, Ir, T, ME.message);
                results = [results; Ir, T, NaN, NaN, NaN];
            end
            
        end
    end
    
    % Save results to CSV
    T_results = array2table(results, 'VariableNames', {'Irradiance','Temperature','V_PV','I_PV','P_PV'});
    writetable(T_results, fault_name + ".csv");
    fprintf('CSV saved: %s.csv\n', fault_name);
    
end
