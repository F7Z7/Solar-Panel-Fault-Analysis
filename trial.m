model = 'base_model_solar';
load_system(model);

% Define a single pair of irradiance and temperature
Ir = 1000;   % example value, change as needed
T = 25;     % example value, change as needed

% Assign values to workspace
assignin("base", "Ir", Ir);
assignin("base", "T", T);

try
    % Run the simulation
    simOut = sim(model, ...
        'StartTime', '0', ...
        'StopTime', '0.5', ...
        'Solver', 'ode23tb', ...
        'MaxStep', '1e-6', ...
        'RelTol', '1e-3', ...
        'AbsTol', '1e-4');

    V_PV = NaN; I_PV = NaN;

    % Extract outputs
    V_PV_data = simOut.get("V_PV");
    if isnumeric(V_PV_data) && ~isempty(V_PV_data)
        V_PV = V_PV_data(end);
    end

    I_PV_data = simOut.get("I_PV");
    if isnumeric(I_PV_data) && ~isempty(I_PV_data)
        I_PV = I_PV_data(end);
    end

    % Display result
    if isnan(V_PV) || isnan(I_PV) || isinf(V_PV) || isinf(I_PV) || V_PV <= 0 || I_PV <= 0
        fprintf('Invalid Output at (V=%.2f I=%.2f) for Ir=%4.0f T=%2.0f\n', V_PV, I_PV, Ir, T);
    else
        fprintf('Success: Ir=%4.0f T=%2.0f — (V=%.2f I=%.2f)\n', Ir, T, V_PV, I_PV);
    end

catch ME
    fprintf('Simulation failed at Ir=%4.0f, T=%2.0f — Error: %s\n', Ir, T, ME.message);
end
