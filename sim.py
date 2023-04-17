import numpy as np
import matplotlib.pyplot as plt


#sin in plain, parabolic in height
WAVE_AMPLITUDE = 100 #[m]
WAVE_PERIOD = 100 # [s]
VEL_X = 3 # [m/s]
SIM_TIME = 100 # [s]
SIM_FREQUENCY = 1000 # [Hz]
SW_FREQUENCY = 100 # [Hz]
GNSS_STD = 5.5 #[m]
VEL_STD = 5.5 #[m/s]
#this needs to be tuned
PROCESS_NOISE_POS = 2.5
PROCESS_NOISE_VEL = 2.5
MEAS_NOISE_POS = 2.25
MEAS_NOISE_VEL = 2.5

#groundtruth
time = np.linspace(0, SIM_TIME, SIM_FREQUENCY*SIM_TIME) # [s]
#position
x = time*VEL_X
y = WAVE_AMPLITUDE*np.sin(2*np.pi*time/WAVE_PERIOD)
h = np.sqrt(time*100)
#velocity
vel_x = np.diff(x)
vel_x = np.insert(vel_x, 0, 0)
vel_y = np.diff(y)
vel_y = np.insert(vel_y, 0, 0)
vel_h = np.diff(h)
vel_h = np.insert(vel_h, 0, 0)

#generate noisy measurements
measurement_time = np.linspace(0, SIM_TIME, SW_FREQUENCY*SIM_TIME)
x_gnss_noisy = np.random.normal(np.interp(measurement_time, time, x), GNSS_STD)
y_gnss_noisy = np.random.normal(np.interp(measurement_time, time, y), GNSS_STD)
h_gnss_noisy = np.random.normal(np.interp(measurement_time, time, h), GNSS_STD)
vel_x_gnss_noisy = np.random.normal(np.interp(measurement_time, time, vel_x), GNSS_STD)
vel_y_gnss_noisy = np.random.normal(np.interp(measurement_time, time, vel_y), GNSS_STD)
vel_h_gnss_noisy = np.random.normal(np.interp(measurement_time, time, vel_h), GNSS_STD)


############################################
#Kalman
last_filtered_state = np.zeros(6)
last_filtered_state_cov = np.eye(6)
dt = 1 / SW_FREQUENCY
q_matrix = np.array([[PROCESS_NOISE_POS, 0, 0, 0, 0, 0],
                            [0, PROCESS_NOISE_POS, 0, 0, 0, 0],
                            [0, 0, PROCESS_NOISE_POS, 0, 0, 0],
                            [0, 0, 0, PROCESS_NOISE_VEL, 0, 0],
                            [0, 0, 0, 0, PROCESS_NOISE_VEL, 0],
                            [0, 0, 0, 0, 0, PROCESS_NOISE_VEL]])
#measurement model to be updated
h_matrix = np.eye(6)
#measurement noise to be updated
r_matrix = np.array([[MEAS_NOISE_POS, 0, 0, 0, 0, 0],
                            [0, MEAS_NOISE_POS, 0, 0, 0, 0],
                            [0, 0, MEAS_NOISE_POS, 0, 0, 0],
                            [0, 0, 0, MEAS_NOISE_VEL, 0, 0],
                            [0, 0, 0, 0, MEAS_NOISE_VEL, 0],
                            [0, 0, 0, 0, 0, MEAS_NOISE_VEL]])

system_dynamics = np.array([[1, 0, 0, dt, 0, 0],
                            [0, 1, 0, 0, dt, 0],
                            [0, 0, 1, 0, 0, dt],
                            [0, 0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 1]])


filtered_states = np.zeros((6, np.size(measurement_time)))
filtered_state_covs = np.zeros((6, 6, np.size(measurement_time)))
for idx, _ in enumerate(measurement_time):
    #predict
    predicted_state = system_dynamics @ last_filtered_state
    predicted_state_cov = system_dynamics @ last_filtered_state_cov @ system_dynamics.T + q_matrix

    #update
    measurement = np.array([x_gnss_noisy[idx],
                            y_gnss_noisy[idx],
                            h_gnss_noisy[idx],
                            vel_x_gnss_noisy[idx],
                            vel_y_gnss_noisy[idx],
                            vel_h_gnss_noisy[idx]])
    
    #here we need two updates, one GNSS pose if valid, another IMU data if valid, like Nibbler
    #and then sensor fusion, if GNSS is not available (spoofing and jamming) we ride on IMU
    innovation = measurement - h_matrix @ predicted_state
    innovation_cov = h_matrix @ predicted_state_cov @ h_matrix.T + r_matrix
    kalman_gain = predicted_state_cov @ h_matrix.T @ np.linalg.inv(innovation_cov)
    filtered_state = predicted_state + kalman_gain @ measurement
    filtered_state_cov = (np.eye(6) - kalman_gain @ h_matrix) @ predicted_state_cov
    
    filtered_states[:,idx]  = filtered_state
    filtered_state_covs[:, :, idx] = filtered_state_cov



fig, axs = plt.subplots(3)
axs[0].plot(time, x)
axs[0].plot(measurement_time, x_gnss_noisy)
axs[0].plot(measurement_time, filtered_states[0,:])
axs[0].set(xlabel='time, [s]', ylabel='X, [m]')
axs[1].plot(time, y)
axs[1].plot(measurement_time, y_gnss_noisy)
axs[1].plot(measurement_time, filtered_states[1,:])
axs[1].set(xlabel='time, [s]', ylabel='Y, [m]')
axs[2].plot(time, h)
axs[2].plot(measurement_time, h_gnss_noisy)
axs[2].plot(measurement_time, filtered_states[2,:])
axs[2].set(xlabel='time, [s]', ylabel='H, [m]')

plt.show()
