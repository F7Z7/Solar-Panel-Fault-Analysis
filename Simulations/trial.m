% ================================================================
% Script: run_short_circuit_conditions.m
% Purpose: Simulate short_circuit.slx for various irradiance & temperature
% ================================================================

clc; clear; close all;

% --- Define model name ---
model = 'open_circuit.slx';

% Load Simulink model
load_system(model);

% --- Define irradiance and temperature test ranges ---
Ir_values = [200, 400, 600, 800, 1000];   % in W/m^2
T_values  = [15, 25, 35, 45, 55];         % in °C

% --- Initialize result table ---
results = [];

% --- Loop through all combinations ---
for Ir = Ir_values
    for T = T_values

        % Assign to base workspace
        assignin('base', 'Ir', Ir);
        assignin('base', 'T', T);

        try
            % --- Run simulation ---
            simOut = sim(model, ...
                'StartTime', '0', ...
                'StopTime', '0.5', ...
                'Solver', 'ode23tb', ...
                'MaxStep', '1e-6', ...
                'RelTol', '1e-3', ...
                'AbsTol', '1e-4', ...
                'CaptureErrors', 'on');

            % --- Initialize outputs ---
            V_PV = NaN;
            I_PV = NaN;

            % --- Extract results ---
            V_PV_data = simOut.get('V_PV');
            if isnumeric(V_PV_data) && ~isempty(V_PV_data)
                V_PV = V_PV_data(end);
            end

            I_PV_data = simOut.get('I_PV');
            if isnumeric(I_PV_data) && ~isempty(I_PV_data)
                I_PV = I_PV_data(end);
            end

            % --- Display and log result ---
            if isnan(V_PV) || isnan(I_PV) || isinf(V_PV) || isinf(I_PV) || V_PV <= 0 || I_PV <= 0
                fprintf('❌ Invalid Output: Ir=%4.0f, T=%2.0f (V=%.2f, I=%.2f)\n', Ir, T, V_PV, I_PV);
                status = "Invalid";
            else
                fprintf('✅ Success: Ir=%4.0f, T=%2.0f — (V=%.2f, I=%.2f)\n', Ir, T, V_PV, I_PV);
                status = "OK";
            end

        catch ME
            fprintf('⚠️ Simulation failed: Ir=%4.0f, T=%2.0f — %s\n', Ir, T, ME.message);
            V_PV = NaN;
            I_PV = NaN;
            status = "Error";
        end

        % --- Append to results table ---
        results = [results; {Ir, T, V_PV, I_PV, char(status)}];

    end
end

% --- Convert to table ---
results_table = cell2table(results, ...
    'VariableNames', {'Irradiance', 'Temperature', 'V_PV', 'I_PV', 'Status'});

% --- Save results ---
writetable(results_table, 'open_circuit_results.csv');

fprintf('\n✅ Simulation complete! Results saved to open_circuit_results.csv\n');

% --- Optional: close model ---
close_system(model, 0);
