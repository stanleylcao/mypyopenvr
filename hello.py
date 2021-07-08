#!/bin/env python

import sys
import time
import openvr
import pkg_resources
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
from tqdm import tqdm

def original_hello_py_example():
    """
    The original hello.py example.
    """
    print("OpenVR test program")

    if openvr.isHmdPresent():
        print("VR head set found")

    if openvr.isRuntimeInstalled():
        print("Runtime is installed")

    vr_system = openvr.init(openvr.VRApplication_Scene)

    print(openvr.getRuntimePath())

    print(vr_system.getRecommendedRenderTargetSize())

    print(vr_system.isDisplayOnDesktop())

    for i in range(10):
        xform = vr_system.getEyeToHeadTransform(openvr.Eye_Left)
        print(xform)
        sys.stdout.flush()
        time.sleep(0.2)

    openvr.shutdown()

def read_me_example():
    """
    The example within the README.md file.
    """
    breakpoint()
    openvr.init(openvr.VRApplication_Scene)
    poses = []  # will be populated with proper type after first call
    for i in range(100):
        poses, _ = openvr.VRCompositor().waitGetPoses(poses, None)
        hmd_pose = poses[openvr.k_unTrackedDeviceIndex_Hmd]
        print(hmd_pose.mDeviceToAbsoluteTracking)
        sys.stdout.flush()
        time.sleep(0.2)
    openvr.shutdown()

# --- BEGIN MY CODE HERE --- 

def get_position_from_HmdMatrix(hmd_matrix):
    """
    Gets the xyz-position from the HmdMatrix34_t `hmd_matrix` and stores it in the format of an
    HmdVector3_t.
    """
    # Make an instance of HmdVector3_t, which is just an float array of size 3
    vec = openvr.HmdVector3_t()
    vec.v[0] = hmd_matrix.m[0][3] # get x-coordinate
    vec.v[1] = hmd_matrix.m[1][3] # get y-coordinate
    vec.v[2] = hmd_matrix.m[2][3] # get z-coordinate
    return vec

def get_controller_ids(vr_system=None):
    """
    This function surfaces the controller indexes into the `poses` array obtained in line 235
    from the `waitGetPoses(poses, None)` function. Within the `poses` array at the controller
    indexes is a struct that contains position information about the controllers.
    """
    if vr_system is None:
        vr_system = openvr.VRSystem() # get the instance of the already initialized VR system.
    left, right = None, None

    # Get the index for the left and right controllers, using the predefined controller role constants
    left_controller_index \
        = vr_system.getTrackedDeviceIndexForControllerRole(openvr.TrackedControllerRole_LeftHand)
    right_controller_index \
        = vr_system.getTrackedDeviceIndexForControllerRole(openvr.TrackedControllerRole_RightHand)
    return left_controller_index, right_controller_index

# def track_controller_actions(tracked_device_index, tracking_frequency):
#     """
#     This is a draft of a function that would be able to surface the button presses of the valve
#     index controller.
#     """
#     vr_system = openvr.VRSystem()
#     device_class = vr_system.getTrackedDeviceClass(tracked_device_index)
#     if device_class != openvr.TrackedDeviceClass_Controller:
#         print(f'Tracked device index {tracked_device_index} is not a controller')
#         return
#     tracked_controller_role = vr_system.getControllerRoleForTrackedDeviceIndex(tracked_device_index)
#     if tracked_controller_role == openvr.TrackedControllerRole_Invalid:
#         print(f'Tracked device index {tracked_device_index} is not a valid controller')
#     elif tracked_controller_role == openvr.TrackedControllerRole_LeftHand:
#         print('Actions of left hand controller being tracked.')
#     elif tracked_controller_role == openvr.TrackedControllerRole_RightHand:
#         print('Actions of right hand controller being tracked.')
#     else:
#         print('Unsupported controller')
#         return

#     try:
#         last_packet_num = None
#         while True:
#             succeded, controller_state = vr_system.getControllerState(tracked_device_index)
#             if not succeded:
#                 print('Getting controller state unsuccessful. Exiting...')
#                 return
#             if controller_state.unPacketNum != last_packet_num:
#                 last_packet_num = controller_state.unPacketNum
#                 print(f'ulButtonPressed = {controller_state.ulButtonPressed}')
#                 print(f'ulButtonTouched = {controller_state.ulButtonTouched}')
#             time.sleep(1 / tracking_frequency)
#     except KeyboardInterrupt:
#         print("Control+C pressed, shutting down...")
#         openvr.shutdown()

def append_coordinates(x_coords, y_coords, z_coords, ordered_triple):
    """
    Appends the coordinates of the ordered_triple to the lists. This is mainly used to manipulate
    the data for matplotlib.
    """
    x_coords.append(ordered_triple[0])
    y_coords.append(ordered_triple[1])
    z_coords.append(ordered_triple[2])

# Dictionary for turning the finger index into a string.
finger_index_dictionary = {
    openvr.VRFinger_Thumb: 'thumb (1)',
    openvr.VRFinger_Index: 'index (2)',
    openvr.VRFinger_Middle: 'middle (3)',
    openvr.VRFinger_Ring: 'ring (4)',
    openvr.VRFinger_Pinky: 'pinky (5)',
}    

# Dictionary for turning the splay (i.e., distance between two fingers) into a string.
finger_splay_dictionary = {
    openvr.VRFingerSplay_Thumb_Index: 'thumb-index (1-2)',
    openvr.VRFingerSplay_Index_Middle: 'index-middle (2-3)',
    openvr.VRFingerSplay_Middle_Ring: 'middle-ring (3-4)',
    openvr.VRFingerSplay_Ring_Pinky: 'ring-pinky (4-5)'
}   

def print_skeletal_curl_and_splay(skeletal_summary_data):
    """
    Prints out the data for each finger in the VRSkeletalSummaryData_t struct
    """
    # Print curl data (i.e., how curled each finger is)
    for finger_index in range(openvr.VRFinger_Count): # 0 to 5 is thumb to pinky
        finger_curl = skeletal_summary_data.flFingerCurl[finger_index]
        print(f'Curl of {finger_index_dictionary[finger_index]} = {finger_curl}')

    # Print splay data
    for finger_splay_index in range(openvr.VRFingerSplay_Count): # 0 to 4 is thumb-index to ring-pinky
        finger_splay = skeletal_summary_data.flFingerSplay[finger_splay_index]
        print(f'Splay between {finger_splay_dictionary[finger_splay_index]} = {finger_splay}')
        

def track_skeletal_summary_data():
    """
    Gets all the the summary of the skeletal data, which notably includes the degree of finger
    curling and finger separation.
    """
    # Get the action path for `hello_actions.json`, which is the JSON file that is used in this
    # example. Note that this is not the same as `hellovr_actions.json`, which is the JSON file used
    # in line 213 of `hellovr_glfw.py`
    action_path = pkg_resources.resource_filename('samples', 'hello_actions.json')
    # Set the action manifest path to read in the JSON file
    openvr.VRInput().setActionManifestPath(action_path)
    # debugging print statement to demonstrate that an absolute path is obtained to feed into
    # getAction(Set)?Handle
    print(action_path)
    # Get the action (set)? handle from the action path specified in the `hello_actions.json` file.
    left_controller_action_handle = openvr.VRInput().getActionSetHandle('/actions/default/in/SkeletonLeftHand')
    right_controller_action_handle = openvr.VRInput().getActionSetHandle('/actions/default/in/SkeletonRightHand')
    print(left_controller_action_handle, right_controller_action_handle) # for debugging
    
    # Could use openvr.VRSummaryType_FromDevice instead for lower latency. FromAnimation means that
    # skeletal summary data is obtained from the animation, rather than directly from the device's
    # sensors.
    summary_type = openvr.VRSummaryType_FromDevice # set the summary type
    # Get skeletal summary data for both right and left controllers
    left_skeletal_summary_data = openvr.VRInput().getSkeletalSummaryData(left_controller_action_handle, summary_type)
    right_skeletal_summary_data = openvr.VRInput().getSkeletalSummaryData(right_controller_action_handle, summary_type)
    
    # Begin tracking the skeletal curl and splay
    try:
        while True:
            print_skeletal_curl_and_splay(left_skeletal_summary_data)
            print_skeletal_curl_and_splay(right_skeletal_summary_data)
    except KeyboardInterrupt:
        print("Control+C pressed, shutting down...")
        openvr.shutdown()

def connect_controllers(vr_system=None):
    """
    This function executes all the logic to wait until both the left and right controllers are
    connected.
    """
    # If VR system is not passed in, assign vr_system variable to the current instance of the system
    if vr_system is None:
        vr_system = openvr.VRSystem()
    left_index, right_index = get_controller_ids(vr_system)
    try:
        while (left_index == openvr.k_unTrackedDeviceIndexInvalid
                or right_index == openvr.k_unTrackedDeviceIndexInvalid):
            left_index, right_index = get_controller_ids(vr_system)
            print("Waiting for controllers...")
            time.sleep(2.0)
    except KeyboardInterrupt:
        print("Control+C pressed, shutting down...")
        openvr.shutdown()
        exit(0)
    return left_index, right_index

def trackVRSet(vr_system=None):
    """
    Tracks the xyz-position data for the headset and controller.
    """
    print("===========================")
    print("Waiting for controllers...")
    left_index, right_index = connect_controllers()
    print('Controllers Found!')
    print("Left controller ID: " + str(left_index))
    print("Right controller ID: " + str(right_index))
    print("===========================")

    track_skeletal_summary_data()
    
    # CODE FOR TRACKING XYZ POSITION DATA BELOW - COMMENTED OUT FOR SIMPLICITY

    # print(openvr.k_unTrackedDeviceIndexInvalid)
    # track_controller_actions(left_index, 1)

    # poses = []  # will be populated with proper type after first call
    # hmd_x, hmd_y, hmd_z = [], [], []
    # left_x, left_y, left_z = [], [], []
    # right_x, right_y, right_z = [], [], []

    # print('Tracking...')
    # for _ in tqdm(range(1000)):
    #     poses, _ = openvr.VRCompositor().waitGetPoses(poses, None)
    #     hmd_pose = poses[openvr.k_unTrackedDeviceIndex_Hmd] # get HmdMatrix34_t for hmd
    #     left_controller_pose = poses[left_index] # get HmdMatrix34_t for left controller
    #     right_controller_pose = poses[right_index] # get HmdMatrix34_t for right controller

    #     hmd_position_vec = get_position_from_HmdMatrix(hmd_pose.mDeviceToAbsoluteTracking)
    #     # print('HMD:', hmd_position_vec)
    #     append_coordinates(hmd_x, hmd_y, hmd_z, hmd_position_vec)

    #     left_controller_position_vec = get_position_from_HmdMatrix(left_controller_pose.mDeviceToAbsoluteTracking)
    #     # print('Left:', left_controller_position_vec)
    #     append_coordinates(left_x, left_y, left_z, left_controller_position_vec)

    #     right_controller_position_vec = get_position_from_HmdMatrix(right_controller_pose.mDeviceToAbsoluteTracking)
    #     # print('Right:', right_controller_position_vec)
    #     append_coordinates(right_x, right_y, right_z, right_controller_position_vec)
    #     # print('.', end='')
    #     # sys.stdout.flush()
    #     # time.sleep(1)
    # hmd_fig = plt.figure()
    # hmd_ax = plt.axes(projection = '3d')
    # # hmd_ax.axes.set_xlim3d(left=0, right=2) 
    # # hmd_ax.axes.set_ylim3d(bottom=0, top=2) 
    # # hmd_ax.axes.set_zlim3d(bottom=0, top=2) 
    # hmd_ax.scatter3D(hmd_x, hmd_y, hmd_z, color = "green")
    # plt.show()

    openvr.shutdown()

def main():
    print("===========================")
    print("Initializing OpenVR...")
    try:
        # Initialize openvr system (i.e., boot up SteamVR)
        vr_system = openvr.init(openvr.VRApplication_Scene)
    except openvr.OpenVRError as e:
        print("Error when initializing OpenVR")
        print(e)
        exit(0)
    print('OpenVR initialization successful')
    # Begin tracking the VR system, which now consists of attempting to only surface the skeletal data
    trackVRSet(vr_system)

if __name__ == '__main__':
    # original_hello_py_example()
    # read_me_example()
    main()
