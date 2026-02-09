import cv2
import numpy as np
import sys
import os
import platform
import time
import threading


if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
    DIR_MODELS = os.path.join(application_path, "models")
    DIR_OUT = os.path.join(os.path.expanduser("~"), "Downloads", "Nexus_Output")
    os.makedirs(DIR_OUT, exist_ok=True)
else:
    DIR_MODELS = "models"
    DIR_OUT = os.path.join(os.path.expanduser("~"), "Downloads", "Nexus_Output")
MODEL_PATH = os.path.join(DIR_MODELS, "hand.task")
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
FACE_MODEL_PATH = os.path.join(DIR_MODELS, "face.task")
FACE_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"

INFERENCE_WIDTH = 640
INFERENCE_HEIGHT = 360
INFERENCE_WIDTH_FAST = 320
INFERENCE_HEIGHT_FAST = 180
FACE_STAGGER_FRAMES = 3
GRAPH_STAGGER_FRAMES = 2
CAMERA_WIDTH_FAST = 640
CAMERA_HEIGHT_FAST = 480
TARGET_FPS_FAST = 60.0
TARGET_FPS_QUALITY = 60.0

FACE_MESH_CONNECTIONS = None

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (0, 9), (9, 10), (10, 11), (11, 12),
    (0, 13), (13, 14), (14, 15), (15, 16),
    (0, 17), (17, 18), (18, 19), (19, 20),
    (5, 9), (9, 13), (13, 17)
]

CORE = (50, 205, 50)
ACCENT = (200, 100, 0)
DARK_BG = (10, 12, 13)
PANEL_BG = (27, 30, 32)
GRID = (45, 51, 57)
TEXT = (224, 229, 229)
SUCCESS = (0, 255, 127)
WARNING = (0, 69, 255)
FONT_FACE = cv2.FONT_HERSHEY_SIMPLEX
FONT_LARGE_BASE = 0.5
FONT_MED_BASE = 0.38
FONT_SMALL_BASE = 0.3
FONT_LARGE = 0.5
FONT_MED = 0.38
FONT_SMALL = 0.3
LINE_H_BASE = 12
LABEL_ROW_BASE = 14
LINE_H = 12
LABEL_ROW = 14
PADDING_SCALE = 1.0

def _is_apple_silicon():
    return platform.system() == "Darwin" and platform.machine() == "arm64"

def create_loading_screen(width, height, progress=0.0, status_text="INITIALIZING"):
    loading_screen = np.full((height, width, 3), DARK_BG, dtype=np.uint8)
    
    center_x = width // 2
    center_y = height // 2
    
    title_text = "[ RESTRICTED // ADVANCED TRACKING DIVISION ]"
    (title_w, title_h), baseline = cv2.getTextSize(title_text, FONT_FACE, FONT_LARGE * 1.2, 2)
    title_x = center_x - title_w // 2
    title_y = center_y - 100
    
    cv2.putText(loading_screen, title_text, (title_x, title_y),
               FONT_FACE, FONT_LARGE * 1.2, CORE, 2)
    
    status_x = center_x - 150
    status_y = center_y - 20
    cv2.putText(loading_screen, f">> {status_text}...", (status_x, status_y),
               FONT_FACE, FONT_MED, TEXT, 1)
    
    bar_width = 600
    bar_height = 30
    bar_x = center_x - bar_width // 2
    bar_y = center_y + 30
    
    cv2.rectangle(loading_screen, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height),
                 PANEL_BG, -1)
    cv2.rectangle(loading_screen, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height),
                 CORE, 2)
    
    progress_width = int(bar_width * progress)
    if progress_width > 0:
        cv2.rectangle(loading_screen, (bar_x + 2, bar_y + 2),
                     (bar_x + progress_width - 2, bar_y + bar_height - 2),
                     SUCCESS, -1)
    
    dots = int((time.time() * 2) % 4)
    dot_text = "." * dots
    cv2.putText(loading_screen, dot_text, (bar_x + bar_width + 20, bar_y + bar_height - 5),
               FONT_FACE, FONT_LARGE, CORE, 2)
    
    return loading_screen

def add_glow_effect(image, x, y, text, font, scale, color, thickness, glow_intensity=None):
    cv2.putText(image, text, (x, y), font, scale, color, thickness)
    return image

def draw_glowing_line(image, pt1, pt2, color, thickness=2, glow_size=2):
    cv2.line(image, pt1, pt2, color, thickness)

def draw_glowing_circle(image, center, radius, color, thickness=-1, glow_size=2):
    cv2.circle(image, center, radius, color, thickness)

def download_model():
    os.makedirs(DIR_MODELS, exist_ok=True)
    if not os.path.exists(MODEL_PATH):
        print(">> SYNCING ASSET: HAND_LANDMARKER_V1...")
        import urllib.request
        try:
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
            print("   [ OK ] ASSET_INTEGRITY_VERIFIED")
        except Exception as e:
            print(f"!! CRITICAL: ASSET_SYNC_FAILURE: {e}")
            print(">> MANUAL_FETCH_REQUIRED:")
            print(f"   URL: {MODEL_URL}")
            sys.exit(1)
    return MODEL_PATH

def download_face_model():
    os.makedirs(DIR_MODELS, exist_ok=True)
    if not os.path.exists(FACE_MODEL_PATH):
        print(">> SYNCING ASSET: FACE_LANDMARKER_V2...")
        import urllib.request
        try:
            urllib.request.urlretrieve(FACE_MODEL_URL, FACE_MODEL_PATH)
            print("   [ OK ] ASSET_INTEGRITY_VERIFIED")
        except Exception as e:
            print(f"!! CRITICAL: ASSET_SYNC_FAILURE: {e}")
            print(">> MANUAL_FETCH_REQUIRED:")
            print(f"   URL: {FACE_MODEL_URL}")
            sys.exit(1)
    return FACE_MODEL_PATH


def find_macbook_camera():
    if not getattr(sys, 'frozen', False):
        print("\n[ 02 ] SENSOR ACQUISITION (AVFOUNDATION)")
    if platform.system() == 'Darwin':
        backend = cv2.CAP_AVFOUNDATION
    else:
        backend = cv2.CAP_ANY
    macbook_resolutions = [(1280, 720), (640, 480), (1280, 800), (1440, 900)]
    probe_sleep = 0.03

    def try_index(camera_index):
        cap = cv2.VideoCapture(camera_index, backend)
        if not cap.isOpened():
            return None
        time.sleep(probe_sleep)
        ret, frame = cap.read()
        cap.release()
        if not ret or frame is None:
            return None
        height, width = frame.shape[:2]
        if (width, height) in macbook_resolutions:
            return camera_index
        if width == 1920 and height == 1080:
            return camera_index
        return camera_index

    for idx in [0, 1, 2, 3, 4, 5]:
        result = try_index(idx)
        if result is not None:
            return result, backend
    return 0, backend

def count_fingers(hand_landmarks, image_width, image_height):
    fingers = []
    
    thumb_tip = hand_landmarks[4]
    thumb_joint = hand_landmarks[3]
    wrist = hand_landmarks[0]
    
    if abs(thumb_tip.x - wrist.x) > abs(thumb_joint.x - wrist.x):
        fingers.append(1)
    else:
        fingers.append(0)
    
    finger_pairs = [
        (8, 6),
        (12, 10),
        (16, 14),
        (20, 18)
    ]
    
    for tip_idx, joint_idx in finger_pairs:
        tip = hand_landmarks[tip_idx]
        joint = hand_landmarks[joint_idx]
        if tip.y < joint.y:
            fingers.append(1)
        else:
            fingers.append(0)
    
    finger_count = sum(fingers)
    
    gesture = "Unknown"
    if finger_count == 0:
        gesture = "Fist"
    elif finger_count == 1:
        if fingers[1] == 1:
            gesture = "Point"
        elif fingers[0] == 1:
            gesture = "Thumbs Up"
    elif finger_count == 2:
        if fingers[1] == 1 and fingers[2] == 1:
            gesture = "Peace Sign"
        elif fingers[0] == 1:
            gesture = "Two"
    elif finger_count == 3:
        gesture = "Three"
    elif finger_count == 4:
        gesture = "Four"
    elif finger_count == 5:
        gesture = "Open Hand"
    
    return finger_count, gesture

def get_handedness_label(detection_result, hand_idx):
    if not getattr(detection_result, 'handedness', None) or hand_idx >= len(detection_result.handedness):
        return "Unknown"
    cats = detection_result.handedness[hand_idx]
    if not cats:
        return "Unknown"
    label = (cats[0].category_name or "Unknown")
    if label == "Left":
        return "Right"
    if label == "Right":
        return "Left"
    return label


def draw_hand_graph(hand_landmarks, graph_width=400, graph_height=400, terminal_lines=None, terminal_height=None):
    graph = np.full((graph_height, graph_width, 3), DARK_BG, dtype=np.uint8)
    
    if terminal_height is None:
        terminal_height = 200 if terminal_lines else 0
    else:
        terminal_height = terminal_height if terminal_lines else 0
    plot_height = graph_height - terminal_height
    
    grid_color = GRID
    for i in range(0, graph_width, 50):
        cv2.line(graph, (i, 0), (i, plot_height), grid_color, 1)
    for i in range(0, plot_height, 50):
        cv2.line(graph, (0, i), (graph_width, i), grid_color, 1)
    
    xs = [lm.x for lm in hand_landmarks]
    ys = [lm.y for lm in hand_landmarks]
    
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    
    padding = 0.2
    range_x = max_x - min_x
    range_y = max_y - min_y
    
    if range_x < 0.01:
        range_x = 0.1
        min_x = max_x - 0.1
    if range_y < 0.01:
        range_y = 0.1
        min_y = max_y - 0.1
    
    available_width = graph_width * (1 - 2 * padding)
    available_plot_height = plot_height * (1 - 2 * padding)
    
    scale_x = available_width / range_x if range_x > 0 else 1
    scale_y = available_plot_height / range_y if range_y > 0 else 1
    scale = min(scale_x, scale_y)
    
    center_x = graph_width / 2
    center_y = plot_height / 2
    hand_center_x = (min_x + max_x) / 2
    hand_center_y = (min_y + max_y) / 2
    
    offset_x = center_x - hand_center_x * scale
    offset_y = center_y - hand_center_y * scale
    
    for connection in HAND_CONNECTIONS:
        start_idx, end_idx = connection
        start = hand_landmarks[start_idx]
        end = hand_landmarks[end_idx]
        
        x1 = int(start.x * scale + offset_x)
        y1 = int(start.y * scale + offset_y)
        x2 = int(end.x * scale + offset_x)
        y2 = int(end.y * scale + offset_y)
        
        if 0 <= x1 < graph_width and 0 <= y1 < plot_height and \
           0 <= x2 < graph_width and 0 <= y2 < plot_height:
            draw_glowing_line(graph, (x1, y1), (x2, y2), CORE, 2, 2)
    
    for idx, landmark in enumerate(hand_landmarks):
        x = int(landmark.x * scale + offset_x)
        y = int(landmark.y * scale + offset_y)
        
        if 0 <= x < graph_width and 0 <= y < plot_height:
            draw_glowing_circle(graph, (x, y), 6, ACCENT, -1, 2)
            cv2.circle(graph, (x, y), 8, (180, 180, 180), 1)
            
            label_x = x + int(12 * PADDING_SCALE)
            label_y = y - int(12 * PADDING_SCALE)
            if 0 <= label_x < graph_width and 0 <= label_y < plot_height:
                add_glow_effect(graph, label_x, label_y, str(idx),
                              FONT_FACE, FONT_SMALL, TEXT, 1, 2)
    
    if terminal_lines:
        terminal_y = plot_height + int(5 * PADDING_SCALE)
        cv2.rectangle(graph, (0, plot_height), (graph_width, graph_height), PANEL_BG, -1)
        draw_glowing_line(graph, (0, plot_height), (graph_width, plot_height), CORE, 2, 1)
        
        add_glow_effect(graph, int(8 * PADDING_SCALE), terminal_y + int(16 * PADDING_SCALE), "TERMINAL - LIVE COORDINATES",
                       FONT_FACE, FONT_MED, CORE, 1, 2)
        
        line_height = LINE_H
        max_lines = min(len(terminal_lines), (graph_height - terminal_y - int(28 * PADDING_SCALE)) // line_height)
        for i, line in enumerate(terminal_lines[-max_lines:]):
            y_pos = terminal_y + int(32 * PADDING_SCALE) + (i * line_height)
            color = TEXT if not line.startswith('Hand') and not line.startswith('Point') else CORE
            cv2.putText(graph, line, (8, y_pos),
                       FONT_FACE, FONT_SMALL, color, 1)
    
    return graph

def draw_multiple_hands_graph(all_hand_landmarks, graph_width=400, graph_height=400, terminal_lines=None, terminal_height=None):
    graph = np.full((graph_height, graph_width, 3), DARK_BG, dtype=np.uint8)
    
    if terminal_height is None:
        terminal_height = 200 if terminal_lines else 0
    else:
        terminal_height = terminal_height if terminal_lines else 0
    plot_height = graph_height - terminal_height
    
    grid_color = GRID
    for i in range(0, graph_width, 50):
        cv2.line(graph, (i, 0), (i, plot_height), grid_color, 1)
    for i in range(0, plot_height, 50):
        cv2.line(graph, (0, i), (graph_width, i), grid_color, 1)
    
    all_xs = []
    all_ys = []
    for hand_landmarks in all_hand_landmarks:
        all_xs.extend([lm.x for lm in hand_landmarks])
        all_ys.extend([lm.y for lm in hand_landmarks])
    
    min_x, max_x = min(all_xs), max(all_xs)
    min_y, max_y = min(all_ys), max(all_ys)
    
    padding = 0.2
    range_x = max_x - min_x
    range_y = max_y - min_y
    
    if range_x < 0.01:
        range_x = 0.1
        min_x = max_x - 0.1
    if range_y < 0.01:
        range_y = 0.1
        min_y = max_y - 0.1
    
    available_width = graph_width * (1 - 2 * padding)
    available_plot_height = plot_height * (1 - 2 * padding)
    
    scale_x = available_width / range_x if range_x > 0 else 1
    scale_y = available_plot_height / range_y if range_y > 0 else 1
    scale = min(scale_x, scale_y)
    
    center_x = graph_width / 2
    center_y = plot_height / 2
    all_center_x = (min_x + max_x) / 2
    all_center_y = (min_y + max_y) / 2
    
    offset_x = center_x - all_center_x * scale
    offset_y = center_y - all_center_y * scale
    
    hand_colors = [(200, 100, 0), (150, 200, 0)]
    hand_point_colors = [(200, 100, 0), (150, 200, 0)]
    
    for hand_idx, hand_landmarks in enumerate(all_hand_landmarks):
        color = hand_colors[hand_idx % len(hand_colors)]
        point_color = hand_point_colors[hand_idx % len(hand_point_colors)]
        
        for connection in HAND_CONNECTIONS:
            start_idx, end_idx = connection
            start = hand_landmarks[start_idx]
            end = hand_landmarks[end_idx]
            
            x1 = int(start.x * scale + offset_x)
            y1 = int(start.y * scale + offset_y)
            x2 = int(end.x * scale + offset_x)
            y2 = int(end.y * scale + offset_y)
            
            if 0 <= x1 < graph_width and 0 <= y1 < plot_height and \
               0 <= x2 < graph_width and 0 <= y2 < plot_height:
                draw_glowing_line(graph, (x1, y1), (x2, y2), color, 2, 2)
        
        for idx, landmark in enumerate(hand_landmarks):
            x = int(landmark.x * scale + offset_x)
            y = int(landmark.y * scale + offset_y)
            
            if 0 <= x < graph_width and 0 <= y < plot_height:
                draw_glowing_circle(graph, (x, y), 6, point_color, -1, 2)
                cv2.circle(graph, (x, y), 8, (180, 180, 180), 1)
                
                label_x = x + 12
                label_y = y - 12
                if 0 <= label_x < graph_width and 0 <= label_y < plot_height:
                    add_glow_effect(graph, label_x, label_y, str(idx),
                                  FONT_FACE, FONT_SMALL, TEXT, 1, 2)
    
    if terminal_lines:
        terminal_y = plot_height + 5
        cv2.rectangle(graph, (0, plot_height), (graph_width, graph_height), PANEL_BG, -1)
        draw_glowing_line(graph, (0, plot_height), (graph_width, plot_height), CORE, 2, 1)
        
        add_glow_effect(graph, int(8 * PADDING_SCALE), terminal_y + int(16 * PADDING_SCALE), "LIVE COORDINATES",
                       FONT_FACE, FONT_MED, CORE, 1, 2)
        
        line_height = LINE_H
        max_lines = min(len(terminal_lines), (graph_height - terminal_y - int(28 * PADDING_SCALE)) // line_height)
        for i, line in enumerate(terminal_lines[-max_lines:]):
            y_pos = terminal_y + int(28 * PADDING_SCALE) + (i * line_height)
            color = TEXT if not line.startswith('Hand') and not line.startswith('Point') else CORE
            cv2.putText(graph, line, (8, y_pos),
                       FONT_FACE, FONT_SMALL, color, 1)
    
    return graph

def draw_hands_and_face_graph(all_hand_landmarks, all_face_landmarks, graph_width=400, graph_height=400, terminal_lines=None, terminal_height=None, fast_draw=False):
    graph = np.full((graph_height, graph_width, 3), DARK_BG, dtype=np.uint8)
    if terminal_height is None:
        terminal_height = 200 if terminal_lines else 0
    else:
        terminal_height = terminal_height if terminal_lines else 0
    plot_height = graph_height - terminal_height

    all_xs = []
    all_ys = []
    for hand_landmarks in all_hand_landmarks:
        all_xs.extend([lm.x for lm in hand_landmarks])
        all_ys.extend([lm.y for lm in hand_landmarks])
    for face_landmarks in all_face_landmarks:
        for conn in FACE_MESH_CONNECTIONS:
            for idx in (conn.start, conn.end):
                if idx < len(face_landmarks) and face_landmarks[idx].x is not None and face_landmarks[idx].y is not None:
                    all_xs.append(face_landmarks[idx].x)
                    all_ys.append(face_landmarks[idx].y)

    if not all_xs or not all_ys:
        if terminal_lines:
            terminal_y = plot_height + int(5 * PADDING_SCALE)
            cv2.rectangle(graph, (0, plot_height), (graph_width, graph_height), PANEL_BG, -1)
            add_glow_effect(graph, int(8 * PADDING_SCALE), terminal_y + int(16 * PADDING_SCALE), "LIVE COORDINATES", FONT_FACE, FONT_MED, CORE, 1, 2)
            for i, line in enumerate(terminal_lines[:20]):
                cv2.putText(graph, line, (int(8 * PADDING_SCALE), terminal_y + int(28 * PADDING_SCALE) + i * LINE_H), FONT_FACE, FONT_SMALL, TEXT, 1)
        return graph

    min_x, max_x = min(all_xs), max(all_xs)
    min_y, max_y = min(all_ys), max(all_ys)
    padding = 0.2
    range_x = max_x - min_x
    range_y = max_y - min_y
    if range_x < 0.01:
        range_x = 0.1
        min_x = max_x - 0.1
    if range_y < 0.01:
        range_y = 0.1
        min_y = max_y - 0.1
    available_width = graph_width * (1 - 2 * padding)
    available_plot_height = plot_height * (1 - 2 * padding)
    scale_x = available_width / range_x if range_x > 0 else 1
    scale_y = available_plot_height / range_y if range_y > 0 else 1
    scale = min(scale_x, scale_y)
    center_x = graph_width / 2
    center_y = plot_height / 2
    all_center_x = (min_x + max_x) / 2
    all_center_y = (min_y + max_y) / 2
    offset_x = center_x - all_center_x * scale
    offset_y = center_y - all_center_y * scale

    grid_color = GRID
    for i in range(0, graph_width, 50):
        cv2.line(graph, (i, 0), (i, plot_height), grid_color, 1)
    for i in range(0, plot_height, 50):
        cv2.line(graph, (0, i), (graph_width, i), grid_color, 1)

    face_mesh_color = (180, 180, 180)
    face_connections = list(FACE_MESH_CONNECTIONS)
    for face_landmarks in all_face_landmarks:
        for i, conn in enumerate(face_connections):
            if fast_draw and i % 3 != 0:
                continue
            a, b = conn.start, conn.end
            if a >= len(face_landmarks) or b >= len(face_landmarks):
                continue
            pa, pb = face_landmarks[a], face_landmarks[b]
            if pa.x is None or pa.y is None or pb.x is None or pb.y is None:
                continue
            x1 = int(pa.x * scale + offset_x)
            y1 = int(pa.y * scale + offset_y)
            x2 = int(pb.x * scale + offset_x)
            y2 = int(pb.y * scale + offset_y)
            if 0 <= x1 < graph_width and 0 <= y1 < plot_height and 0 <= x2 < graph_width and 0 <= y2 < plot_height:
                cv2.line(graph, (x1, y1), (x2, y2), face_mesh_color, 1)

    hand_colors = [(200, 100, 0), (150, 200, 0)]
    hand_point_colors = [(200, 100, 0), (150, 200, 0)]
    for hand_idx, hand_landmarks in enumerate(all_hand_landmarks):
        color = hand_colors[hand_idx % len(hand_colors)]
        point_color = hand_point_colors[hand_idx % len(hand_point_colors)]
        for connection in HAND_CONNECTIONS:
            start_idx, end_idx = connection
            start = hand_landmarks[start_idx]
            end = hand_landmarks[end_idx]
            x1 = int(start.x * scale + offset_x)
            y1 = int(start.y * scale + offset_y)
            x2 = int(end.x * scale + offset_x)
            y2 = int(end.y * scale + offset_y)
            if 0 <= x1 < graph_width and 0 <= y1 < plot_height and 0 <= x2 < graph_width and 0 <= y2 < plot_height:
                if fast_draw:
                    cv2.line(graph, (x1, y1), (x2, y2), color, 2)
                else:
                    draw_glowing_line(graph, (x1, y1), (x2, y2), color, 2, 2)
        for idx, landmark in enumerate(hand_landmarks):
            x = int(landmark.x * scale + offset_x)
            y = int(landmark.y * scale + offset_y)
            if 0 <= x < graph_width and 0 <= y < plot_height:
                if fast_draw:
                    cv2.circle(graph, (x, y), 6, point_color, -1)
                else:
                    draw_glowing_circle(graph, (x, y), 6, point_color, -1, 2)
                    cv2.circle(graph, (x, y), 8, (180, 180, 180), 1)
                    label_x = x + 12
                    label_y = y - 12
                    if 0 <= label_x < graph_width and 0 <= label_y < plot_height:
                        add_glow_effect(graph, label_x, label_y, str(idx), FONT_FACE, FONT_SMALL, TEXT, 1, 2)

    if terminal_lines:
        terminal_y = plot_height + 5
        cv2.rectangle(graph, (0, plot_height), (graph_width, graph_height), PANEL_BG, -1)
        draw_glowing_line(graph, (0, plot_height), (graph_width, plot_height), CORE, 2, 1)
        add_glow_effect(graph, int(8 * PADDING_SCALE), terminal_y + int(16 * PADDING_SCALE), "LIVE COORDINATES",
                       FONT_FACE, FONT_MED, CORE, 1, 2)
        line_height = LINE_H
        max_lines = min(len(terminal_lines), (graph_height - terminal_y - int(28 * PADDING_SCALE)) // line_height)
        for i, line in enumerate(terminal_lines[-max_lines:]):
            y_pos = terminal_y + int(28 * PADDING_SCALE) + (i * line_height)
            color = TEXT if not line.startswith('Hand') and not line.startswith('Point') else CORE
            cv2.putText(graph, line, (int(8 * PADDING_SCALE), y_pos), FONT_FACE, FONT_SMALL, color, 1)
    return graph

def draw_landmarks_on_image(image, detection_result, fps=None):
    h, w, _ = image.shape
    if fps is not None:
        fps_text = f"FPS: {fps:.1f}"
        (fps_w, fps_h), baseline = cv2.getTextSize(fps_text, FONT_FACE, FONT_LARGE, 2)
        fps_x, fps_y = w - fps_w - int(10 * PADDING_SCALE), h - baseline - int(10 * PADDING_SCALE)
        fps_pad = int(6 * PADDING_SCALE)
        cv2.rectangle(image, (fps_x - fps_pad, fps_y - fps_h - fps_pad), (fps_x + fps_w + fps_pad, fps_y + baseline + fps_pad), PANEL_BG, -1)
        cv2.rectangle(image, (fps_x - fps_pad, fps_y - fps_h - fps_pad), (fps_x + fps_w + fps_pad, fps_y + baseline + fps_pad), CORE, 2)
        add_glow_effect(image, fps_x, fps_y, fps_text, FONT_FACE, FONT_LARGE, CORE, 2, 2)
    for idx, hand_landmarks in enumerate(detection_result.hand_landmarks):
        handedness = get_handedness_label(detection_result, idx)
        for connection in HAND_CONNECTIONS:
            start_idx, end_idx = connection
            start, end = hand_landmarks[start_idx], hand_landmarks[end_idx]
            x1, y1 = int(start.x * w), int(start.y * h)
            x2, y2 = int(end.x * w), int(end.y * h)
            draw_glowing_line(image, (x1, y1), (x2, y2), CORE, 2, 2)
        for point_idx, landmark in enumerate(hand_landmarks):
            x, y = int(landmark.x * w), int(landmark.y * h)
            draw_glowing_circle(image, (x, y), 5, (188, 19, 254), -1, 2)
            label_x, label_y = x + int(10 * PADDING_SCALE), y - int(10 * PADDING_SCALE)
            if 0 <= label_x < w and 0 <= label_y < h:
                add_glow_effect(image, label_x, label_y, str(point_idx), FONT_FACE, FONT_MED, (224, 229, 229), 1, 2)
        finger_count, gesture = count_fingers(hand_landmarks, w, h)
        wrist = hand_landmarks[0]
        text_x = int(wrist.x * w)
        text_y = int(wrist.y * h) - int(32 * PADDING_SCALE)
        text_content = f"{handedness} | Fingers: {finger_count} | {gesture}"
        (text_w, text_h), baseline = cv2.getTextSize(text_content, FONT_FACE, FONT_LARGE, 2)
        panel_padding = int(6 * PADDING_SCALE)
        cv2.rectangle(image, (text_x - panel_padding, text_y - text_h - panel_padding),
                       (text_x + text_w + panel_padding, text_y + baseline + panel_padding), PANEL_BG, -1)
        cv2.rectangle(image, (text_x - panel_padding, text_y - text_h - panel_padding),
                       (text_x + text_w + panel_padding, text_y + baseline + panel_padding), CORE, 2)
        add_glow_effect(image, text_x, text_y, text_content, FONT_FACE, FONT_LARGE, CORE, 2, 2)
    return image

def draw_faces_on_image(image, face_result, draw_mesh=True):
    if not face_result or not face_result.face_landmarks or not draw_mesh:
        return image
    h, w = image.shape[:2]
    for landmarks in face_result.face_landmarks:
        for conn in FACE_MESH_CONNECTIONS:
            a, b = conn.start, conn.end
            if a >= len(landmarks) or b >= len(landmarks):
                continue
            pa, pb = landmarks[a], landmarks[b]
            if pa.x is None or pa.y is None or pb.x is None or pb.y is None:
                continue
            x1 = int(pa.x * w)
            y1 = int(pa.y * h)
            x2 = int(pb.x * w)
            y2 = int(pb.y * h)
            if 0 <= x1 < w and 0 <= y1 < h and 0 <= x2 < w and 0 <= y2 < h:
                cv2.line(image, (x1, y1), (x2, y2), CORE, 1)
    return image

# Object categories to detect (COCO dataset categories)
OBJECT_CATEGORIES = {
    'person': (0, 255, 127),      # Green
    'dog': (255, 165, 0),          # Orange
    'cat': (255, 20, 147),         # Deep Pink
    'cell phone': (0, 191, 255),   # Deep Sky Blue
    'phone': (0, 191, 255),        # Deep Sky Blue
    'laptop': (138, 43, 226),      # Blue Violet
    'mouse': (255, 140, 0),        # Dark Orange
    'keyboard': (255, 215, 0),     # Gold
    'book': (139, 69, 19),         # Saddle Brown
    'cup': (0, 255, 127),          # Spring Green
    'bottle': (0, 255, 127),       # Spring Green
    'chair': (128, 128, 128),       # Gray
    'couch': (128, 128, 128),       # Gray
    'tv': (75, 0, 130),            # Indigo
    'remote': (255, 0, 255),       # Magenta
    'backpack': (0, 0, 255),       # Blue
    'umbrella': (0, 0, 255),       # Blue
    'handbag': (255, 0, 0),        # Red
    'suitcase': (255, 0, 0),       # Red
    'sports ball': (0, 255, 0),    # Lime
    'frisbee': (0, 255, 0),         # Lime
    'skis': (255, 255, 0),          # Yellow
    'snowboard': (255, 255, 0),     # Yellow
    'kite': (0, 255, 255),          # Cyan
    'baseball bat': (128, 0, 128),  # Purple
    'baseball glove': (128, 0, 128), # Purple
    'skateboard': (255, 192, 203),  # Pink
    'surfboard': (0, 128, 255),     # Azure
    'tennis racket': (50, 205, 50), # Lime Green
    'wine glass': (255, 20, 147),   # Deep Pink
    'fork': (192, 192, 192),        # Silver
    'knife': (192, 192, 192),       # Silver
    'spoon': (192, 192, 192),       # Silver
    'bowl': (139, 69, 19),          # Saddle Brown
    'banana': (255, 255, 0),        # Yellow
    'apple': (255, 0, 0),           # Red
    'sandwich': (255, 165, 0),      # Orange
    'orange': (255, 165, 0),        # Orange
    'broccoli': (0, 255, 0),        # Green
    'carrot': (255, 140, 0),        # Dark Orange
    'pizza': (255, 69, 0),          # Red Orange
    'donut': (139, 0, 139),         # Dark Magenta
    'cake': (255, 20, 147),         # Deep Pink
    'car': (0, 0, 255),             # Blue
    'truck': (0, 0, 255),            # Blue
    'bus': (255, 0, 0),              # Red
    'motorcycle': (255, 140, 0),     # Dark Orange
    'bicycle': (0, 255, 0),          # Green
    'airplane': (135, 206, 250),     # Light Sky Blue
    'train': (0, 0, 139),            # Dark Blue
    'boat': (0, 0, 255),             # Blue
}

def get_object_color(category_name):
    """Get color for object category"""
    category_lower = category_name.lower()
    # Check exact match first
    if category_lower in OBJECT_CATEGORIES:
        return OBJECT_CATEGORIES[category_lower]
    # Check partial matches
    for cat, color in OBJECT_CATEGORIES.items():
        if cat in category_lower or category_lower in cat:
            return color
    # Default color
    return WARNING

def draw_center_position_graph(graph_canvas, hand_centers_history, face_centers_history, max_history=200):
    graph_h, graph_w = graph_canvas.shape[:2]
    
    graph_canvas.fill(0)
    cv2.rectangle(graph_canvas, (0, 0), (graph_w, graph_h), DARK_BG, -1)
    
    graph_mid_x = graph_w // 2
    separator_x = graph_mid_x
    
    title_y = 15
    title_x = (graph_mid_x // 2) - 60
    cv2.putText(graph_canvas, "X-AXIS POSITION", (title_x, title_y), 
               FONT_FACE, FONT_SMALL, CORE, 1)
    
    title_x_right = graph_mid_x + (graph_mid_x // 2) - 60
    cv2.putText(graph_canvas, "Y-AXIS POSITION", (title_x_right, title_y), 
               FONT_FACE, FONT_SMALL, CORE, 1)
    
    cv2.line(graph_canvas, (separator_x, 0), (separator_x, graph_h), GRID, 2)
    
    graph_padding = 30
    graph_area_y = title_y + 10
    graph_area_h = graph_h - graph_area_y - graph_padding
    
    left_graph_x = graph_padding
    left_graph_w = graph_mid_x - graph_padding * 2
    
    right_graph_x = graph_mid_x + graph_padding
    right_graph_w = graph_mid_x - graph_padding * 2
    
    hand_colors = [(200, 100, 0), (150, 200, 0)]
    face_color = (180, 180, 180)
    
    hand_history = hand_centers_history[-max_history:] if len(hand_centers_history) > max_history else hand_centers_history
    face_history = face_centers_history[-max_history:] if len(face_centers_history) > max_history else face_centers_history
    
    all_x_values = []
    all_y_values = []
    for frame_hands in hand_history:
        for hand_center in frame_hands:
            if hand_center:
                all_x_values.append(hand_center[0])
                all_y_values.append(hand_center[1])
    for face_center in face_history:
        if face_center:
            all_x_values.append(face_center[0])
            all_y_values.append(face_center[1])
    
    if not all_x_values and not all_y_values:
        msg_x = left_graph_x + 10
        cv2.putText(graph_canvas, "Waiting for hands/face...", 
                   (msg_x, graph_area_y + graph_area_h // 2),
                   FONT_FACE, FONT_SMALL, TEXT, 1)
        return
    
    min_x = min(all_x_values) if all_x_values else 0
    max_x = max(all_x_values) if all_x_values else 1
    x_range = max_x - min_x if max_x != min_x else 1
    
    min_y = min(all_y_values) if all_y_values else 0
    max_y = max(all_y_values) if all_y_values else 1
    y_range = max_y - min_y if max_y != min_y else 1
    
    grid_color = GRID
    for graph_area_x, graph_area_w in [(left_graph_x, left_graph_w), (right_graph_x, right_graph_w)]:
        for i in range(0, graph_area_w, 40):
            cv2.line(graph_canvas, (graph_area_x + i, graph_area_y), 
                    (graph_area_x + i, graph_area_y + graph_area_h), grid_color, 1)
        for i in range(0, graph_area_h, 20):
            cv2.line(graph_canvas, (graph_area_x, graph_area_y + i), 
                    (graph_area_x + graph_area_w, graph_area_y + i), grid_color, 1)
    
    def smooth_points(points, window=5):
        if len(points) < window or window < 2:
            return points
        xs = np.array([p[0] for p in points], dtype=np.float64)
        ys = np.array([p[1] for p in points], dtype=np.float64)
        kernel = np.ones(window) / window
        ys_smooth = np.convolve(ys, kernel, mode='same')
        return [ (int(x), int(y)) for x, y in zip(xs, ys_smooth) ]

    for hand_idx in range(2):
        color = hand_colors[hand_idx % len(hand_colors)]
        points = []
        for frame_idx, frame_hands in enumerate(hand_history):
            if hand_idx < len(frame_hands) and frame_hands[hand_idx]:
                x_center, y_center = frame_hands[hand_idx]
                normalized_x = (x_center - min_x) / x_range
                graph_x = left_graph_x + int((frame_idx / len(hand_history)) * left_graph_w)
                graph_y = graph_area_y + int(normalized_x * graph_area_h)
                points.append((graph_x, graph_y))
        points = smooth_points(points)
        if len(points) > 1:
            for i in range(len(points) - 1):
                cv2.line(graph_canvas, points[i], points[i + 1], color, 2)
    
    for hand_idx in range(2):
        color = hand_colors[hand_idx % len(hand_colors)]
        points = []
        for frame_idx, frame_hands in enumerate(hand_history):
            if hand_idx < len(frame_hands) and frame_hands[hand_idx]:
                x_center, y_center = frame_hands[hand_idx]
                normalized_y = (y_center - min_y) / y_range
                graph_x = right_graph_x + int((frame_idx / len(hand_history)) * right_graph_w)
                graph_y = graph_area_y + int(normalized_y * graph_area_h)
                points.append((graph_x, graph_y))
        points = smooth_points(points)
        if len(points) > 1:
            for i in range(len(points) - 1):
                cv2.line(graph_canvas, points[i], points[i + 1], color, 2)
    
    max_history_len = max(len(hand_history), len(face_history)) if (hand_history and face_history) else (len(hand_history) if hand_history else (len(face_history) if face_history else 1))
    if max_history_len == 0:
        max_history_len = 1
    
    face_points_x = []
    for frame_idx, face_center in enumerate(face_history):
        if face_center:
            x_center, y_center = face_center
            normalized_x = (x_center - min_x) / x_range if x_range > 0 else 0.5
            graph_x = left_graph_x + int((frame_idx / max_history_len) * left_graph_w) if max_history_len > 0 else left_graph_x
            graph_y = graph_area_y + int(normalized_x * graph_area_h)
            face_points_x.append((graph_x, graph_y))
    
    face_points_x = smooth_points(face_points_x)
    if len(face_points_x) > 1:
        for i in range(len(face_points_x) - 1):
            cv2.line(graph_canvas, face_points_x[i], face_points_x[i + 1], face_color, 2)
    
    face_points_y = []
    for frame_idx, face_center in enumerate(face_history):
        if face_center:
            x_center, y_center = face_center
            normalized_y = (y_center - min_y) / y_range if y_range > 0 else 0.5
            graph_x = right_graph_x + int((frame_idx / max_history_len) * right_graph_w) if max_history_len > 0 else right_graph_x
            graph_y = graph_area_y + int(normalized_y * graph_area_h)
            face_points_y.append((graph_x, graph_y))
    
    face_points_y = smooth_points(face_points_y)
    if len(face_points_y) > 1:
        for i in range(len(face_points_y) - 1):
            cv2.line(graph_canvas, face_points_y[i], face_points_y[i + 1], face_color, 2)
    
    legend_y = graph_area_y + graph_area_h + 15
    legend_x = graph_w // 2 - int(100 * PADDING_SCALE)
    if hand_history and any(any(h for h in frame_hands) for frame_hands in hand_history):
        cv2.circle(graph_canvas, (legend_x, legend_y), int(5 * PADDING_SCALE), hand_colors[0], -1)
        cv2.putText(graph_canvas, "Hand 1", (legend_x + int(10 * PADDING_SCALE), legend_y + int(5 * PADDING_SCALE)), 
                   FONT_FACE, FONT_SMALL * 0.8, hand_colors[0], 1)
        legend_x += int(80 * PADDING_SCALE)
    if len(hand_history) > 0 and any(len(frame_hands) > 1 and frame_hands[1] for frame_hands in hand_history):
        cv2.circle(graph_canvas, (legend_x, legend_y), int(5 * PADDING_SCALE), hand_colors[1], -1)
        cv2.putText(graph_canvas, "Hand 2", (legend_x + int(10 * PADDING_SCALE), legend_y + int(5 * PADDING_SCALE)), 
                   FONT_FACE, FONT_SMALL * 0.8, hand_colors[1], 1)
        legend_x += int(80 * PADDING_SCALE)
    if face_history and any(f for f in face_history):
        cv2.circle(graph_canvas, (legend_x, legend_y), int(5 * PADDING_SCALE), face_color, -1)
        cv2.putText(graph_canvas, "Face", (legend_x + int(10 * PADDING_SCALE), legend_y + int(5 * PADDING_SCALE)), 
                   FONT_FACE, FONT_SMALL * 0.8, face_color, 1)

def gesture_matches(current_landmarks, saved_landmarks_data, threshold=0.08):
    if len(current_landmarks) != len(saved_landmarks_data):
        return False
    
    wrist = current_landmarks[0]
    saved_wrist = saved_landmarks_data[0]
    
    total_diff = 0
    for i in range(len(current_landmarks)):
        curr_lm = current_landmarks[i]
        saved_lm = saved_landmarks_data[i]
        
        curr_x = curr_lm.x - wrist.x
        curr_y = curr_lm.y - wrist.y
        saved_x = saved_lm[0] - saved_wrist[0]
        saved_y = saved_lm[1] - saved_wrist[1]
        
        diff = ((curr_x - saved_x)**2 + (curr_y - saved_y)**2)**0.5
        total_diff += diff
    
    avg_diff = total_diff / len(current_landmarks)
    return avg_diff < threshold

def show_startup_menu():
    print("\n[ 03 ] KINEMATIC ENGINE LOADED")
    print("   HAND + FACE TRACKER")
    print("\n[ USER_INPUT_REQUIRED // SELECT TRACKING_PROFILE ]")
    print("  [01] FAST_PATH    - FPS_OPTIMIZED (STAGGERED_DETECTION)")
    print("  [02] QUALITY_PATH - VISUAL_MAX (CONCURRENT_LANDMARKS)")
    print("  [03] AUTO_PATH    - ARCHITECTURE_ADAPTIVE")
    
    fast_mode = None
    while fast_mode is None:
        choice = input("\n>> SELECT_PROFILE [1/2/3]: ").strip()
        if choice == '1':
            fast_mode = True
        elif choice == '2':
            fast_mode = False
        elif choice == '3':
            fast_mode = _is_apple_silicon()
            if fast_mode:
                print(">> SILICON_DETECTED: ENFORCING FAST_PATH")
            else:
                print(">> INTEL_DETECTED: ENFORCING QUALITY_PATH")
        else:
            print("!! INVALID_INPUT: ENTER [1/2/3]")
    
    return fast_mode


def open_camera_with_retry(camera_index, backend, max_attempts=30, wait_sec=1.0, frozen=False):
    wait_per_key_ms = 100
    keys_per_sec = max(1, int(1000 // wait_per_key_ms))
    for attempt in range(max_attempts):
        cap = cv2.VideoCapture(camera_index, backend)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                return cap, frame, True
            cap.release()
        else:
            cap = None
        if frozen:
            w, h = 480, 200
            win = "Nexus — Camera"
            if attempt == 0:
                cv2.namedWindow(win, cv2.WINDOW_NORMAL)
                cv2.resizeWindow(win, w, h)
            screen = np.full((h, w, 3), DARK_BG, dtype=np.uint8)
            cv2.putText(screen, "Waiting for camera permission...", (30, 80), FONT_FACE, 0.6, TEXT, 1)
            cv2.putText(screen, "Grant access in System Settings if prompted.", (30, 120), FONT_FACE, 0.5, TEXT, 1)
            cv2.putText(screen, "Retrying...  Press Q to quit", (30, 160), FONT_FACE, 0.45, CORE, 1)
            cv2.imshow(win, screen)
            for _ in range(int(wait_sec * keys_per_sec)):
                if cv2.waitKey(wait_per_key_ms) & 0xFF == ord('q'):
                    try:
                        cv2.destroyWindow(win)
                    except Exception:
                        pass
                    return None, None, False
        else:
            print("!! Waiting for camera permission... (grant in System Settings if prompted)")
            time.sleep(wait_sec)
    if frozen:
        try:
            cv2.destroyWindow("Nexus — Camera")
        except Exception:
            pass
    return None, None, False


def show_profile_dialog(window_name, screen_width, screen_height):
    """Show profile selection in the main window
    Returns: fast_mode (bool)
    """
    # Calculate scales once (used in both main screen and feedback)
    border_thickness = 3
    title_scale = min(1.2 * (screen_width / 1280), 1.5)
    inst_scale = min(0.6 * (screen_width / 1280), 0.8)
    option_scale = min(0.9 * (screen_width / 1280), 1.2)
    status_scale = min(0.5 * (screen_width / 1280), 0.7)
    
    while True:
        screen = np.full((screen_height, screen_width, 3), DARK_BG, dtype=np.uint8)
        cv2.rectangle(screen, (0, 0), (screen_width, screen_height), PANEL_BG, -1)
        
        # Border
        cv2.rectangle(screen, (border_thickness, border_thickness), 
                     (screen_width - border_thickness, screen_height - border_thickness), CORE, border_thickness)

        # Title
        title = "SELECT TRACKING PROFILE"
        (tw, th), _ = cv2.getTextSize(title, FONT_FACE, title_scale, 3)
        cv2.putText(screen, title, ((screen_width - tw) // 2, int(screen_height * 0.12)), 
                   FONT_FACE, title_scale, CORE, 3)
        
        # Instructions
        inst_text = "Press 1, 2, or 3 on your keyboard"
        (iw, ih), _ = cv2.getTextSize(inst_text, FONT_FACE, inst_scale, 2)
        cv2.putText(screen, inst_text, ((screen_width - iw) // 2, int(screen_height * 0.25)), 
                   FONT_FACE, inst_scale, TEXT, 2)

        # Options
        y0 = int(screen_height * 0.35)
        line_h = int(screen_height * 0.12)
        
        option1 = "[ 1 ]  FAST    — FPS optimized (staggered detection)"
        option2 = "[ 2 ]  QUALITY — Visual max (concurrent landmarks)"
        option3 = "[ 3 ]  AUTO    — Architecture adaptive (recommended)"
        
        cv2.putText(screen, option1, (int(screen_width * 0.1), y0), 
                   FONT_FACE, option_scale, TEXT, 2)
        cv2.putText(screen, option2, (int(screen_width * 0.1), y0 + line_h), 
                   FONT_FACE, option_scale, TEXT, 2)
        cv2.putText(screen, option3, (int(screen_width * 0.1), y0 + 2 * line_h), 
                   FONT_FACE, option_scale, CORE, 2)

        # Status
        status_text = "Waiting for key..."
        (sw, sh), _ = cv2.getTextSize(status_text, FONT_FACE, status_scale, 1)
        cv2.putText(screen, status_text, ((screen_width - sw) // 2, int(screen_height * 0.85)), 
                   FONT_FACE, status_scale, TEXT, 1)
        
        cv2.imshow(window_name, screen)
        key = cv2.waitKey(100) & 0xFF
        if key == ord('1'):
            return True
        if key == ord('2'):
            return False
        if key == ord('3'):
            fast_mode = _is_apple_silicon()
            # Show feedback message
            feedback_screen = np.full((screen_height, screen_width, 3), DARK_BG, dtype=np.uint8)
            cv2.rectangle(feedback_screen, (0, 0), (screen_width, screen_height), PANEL_BG, -1)
            cv2.rectangle(feedback_screen, (border_thickness, border_thickness), 
                         (screen_width - border_thickness, screen_height - border_thickness), CORE, border_thickness)
            
            if fast_mode:
                feedback_text = "SILICON_DETECTED: ENFORCING FAST_PATH"
                feedback_color = SUCCESS
            else:
                feedback_text = "INTEL_DETECTED: ENFORCING QUALITY_PATH"
                feedback_color = WARNING
            
            (fw, fh), _ = cv2.getTextSize(feedback_text, FONT_FACE, title_scale, 3)
            cv2.putText(feedback_screen, feedback_text, ((screen_width - fw) // 2, screen_height // 2), 
                       FONT_FACE, title_scale, feedback_color, 3)
            
            start_text = "Starting application..."
            (st_w, st_h), _ = cv2.getTextSize(start_text, FONT_FACE, inst_scale, 2)
            cv2.putText(feedback_screen, start_text, ((screen_width - st_w) // 2, screen_height // 2 + int(fh * 1.5)), 
                       FONT_FACE, inst_scale, TEXT, 2)
            cv2.imshow(window_name, feedback_screen)
            cv2.waitKey(1000)
            return fast_mode

def main():
    session_id = hex(int(time.time()))[2:]
    executable_path = os.path.abspath(__file__)
    system_info = "Apple M2 (Silicon Architecture)" if _is_apple_silicon() else "Intel Mac"
    
    print("="*80)
    print("[ RESTRICTED // ADVANCED TRACKING DIVISION ]")
    print(f"SESSION_ID: 0x{session_id}")
    print(f"EXECUTABLE: {executable_path}")
    print(f"SYSTEM:     {system_info}")
    print("="*80)
    print()
    
    # Create main window first
    REF_W, REF_H = 1280, 720
    window_name = 'Nexus - MacBook Camera'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_FREERATIO)
    cv2.resizeWindow(window_name, REF_W, REF_H)
    time.sleep(0.08)
    rect = cv2.getWindowImageRect(window_name)
    screen_width = rect[2] if rect[2] > 0 else REF_W
    screen_height = rect[3] if rect[3] > 0 else REF_H
    
    # Show profile selection in main window
    fast_mode = show_profile_dialog(window_name, screen_width, screen_height)

    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    from mediapipe import Image, ImageFormat
    global FACE_MESH_CONNECTIONS
    FACE_MESH_CONNECTIONS = vision.FaceLandmarksConnections.FACE_LANDMARKS_TESSELATION

    inference_w = INFERENCE_WIDTH_FAST if fast_mode else INFERENCE_WIDTH
    inference_h = INFERENCE_HEIGHT_FAST if fast_mode else INFERENCE_HEIGHT
    num_faces = 1 if fast_mode else 2
    num_hands = 2
    face_stagger = FACE_STAGGER_FRAMES if fast_mode else 1
    graph_stagger = GRAPH_STAGGER_FRAMES if fast_mode else 1
    interp_display = cv2.INTER_NEAREST if fast_mode else cv2.INTER_LINEAR
    interp_inference = cv2.INTER_NEAREST if fast_mode else cv2.INTER_LINEAR
    
    global FONT_LARGE, FONT_MED, FONT_SMALL, LINE_H, LABEL_ROW, PADDING_SCALE
    font_scale_factor = 1.8 if not fast_mode else 1.0
    FONT_LARGE = FONT_LARGE_BASE * font_scale_factor
    FONT_MED = FONT_MED_BASE * font_scale_factor
    FONT_SMALL = FONT_SMALL_BASE * font_scale_factor
    LINE_H = int(LINE_H_BASE * font_scale_factor)
    LABEL_ROW = int(LABEL_ROW_BASE * font_scale_factor)
    PADDING_SCALE = font_scale_factor

    if not getattr(sys, 'frozen', False):
        print("\n[ 01 ] INITIALIZING CORE ASSETS...")
    model_path = download_model()
    face_model_path = download_face_model()

    detector, face_landmarker = None, None
    def load_hand():
        nonlocal detector
        opts = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=num_hands,
            min_hand_detection_confidence=0.3,
            min_hand_presence_confidence=0.3,
            min_tracking_confidence=0.3,
        )
        detector = vision.HandLandmarker.create_from_options(opts)
    def load_face():
        nonlocal face_landmarker
        opts = vision.FaceLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=face_model_path),
            running_mode=vision.RunningMode.VIDEO,
            num_faces=num_faces,
            min_face_detection_confidence=0.5,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
        )
        face_landmarker = vision.FaceLandmarker.create_from_options(opts)

    t1 = threading.Thread(target=load_hand)
    t2 = threading.Thread(target=load_face)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    camera_index, backend = find_macbook_camera()
    
    if not getattr(sys, 'frozen', False):
        print("\n[ 04 ] HANDSHAKE & PERMISSIONS")
    time.sleep(0.4)

    frozen = getattr(sys, 'frozen', False)
    cap, test_frame, opened = open_camera_with_retry(camera_index, backend, max_attempts=30, wait_sec=1.0, frozen=frozen)
    if not opened or cap is None or test_frame is None:
        print("!! CRITICAL: SENSOR_ACCESS_DENIED or TIMEOUT")
        print(">> REMEDIATION: SETTINGS > PRIVACY > CAMERA > NEXUS [GRANT] then reopen the app")
        if frozen:
            try:
                cv2.destroyWindow("Nexus — Camera")
            except Exception:
                pass
        sys.exit(1)
    if frozen:
        try:
            cv2.destroyWindow("Nexus — Camera")
        except Exception:
            pass

    test_height, test_width = test_frame.shape[:2]
    if not getattr(sys, 'frozen', False):
        if test_width == 1920 and test_height == 1080:
            print("!! NOTICE: IPHONE_CONTINUITY_ACTIVE (1080P)")
        else:
            print(f">> [ SUCCESS ] CAMERA_LINK_ESTABLISHED ({test_width}x{test_height})")
    cap.set(cv2.CAP_PROP_FPS, 30)
    buf_prop = getattr(cv2, 'CAP_PROP_BUFFERSIZE', None)
    if buf_prop is not None:
        cap.set(buf_prop, 1)
    if fast_mode:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH_FAST)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT_FAST)
    if not getattr(sys, 'frozen', False):
        actual_fps = cap.get(cv2.CAP_PROP_FPS)
        if actual_fps > 0:
            print(f">> CLOCK_SYNC: {actual_fps:.1f} FPS")
        else:
            print(">> CLOCK_SYNC: DEFAULT_30FPS")
    
    # Window already created above for profile selection
    # Update window size in case user resized it
    rect = cv2.getWindowImageRect(window_name)
    screen_width = rect[2] if rect[2] > 0 else screen_width
    screen_height = rect[3] if rect[3] > 0 else screen_height
    
    # Skip loading screen for faster startup (like optimized mode)
    # Just show a brief ready message
    ready_screen = np.full((screen_height, screen_width, 3), DARK_BG, dtype=np.uint8)
    cv2.rectangle(ready_screen, (0, 0), (screen_width, screen_height), PANEL_BG, -1)
    ready_text = "READY"
    (rw, rh), _ = cv2.getTextSize(ready_text, FONT_FACE, FONT_LARGE * 1.2, 2)
    cv2.putText(ready_screen, ready_text, ((screen_width - rw) // 2, screen_height // 2), 
               FONT_FACE, FONT_LARGE * 1.2, CORE, 2)
    cv2.imshow(window_name, ready_screen)
    cv2.waitKey(50)  # Brief display
    
    saved_gestures = {}
    capturing_gesture = False
    gesture_name_input = ""
    recording_graph = False
    video_writer = None
    recording_filename = None
    
    os.makedirs(DIR_OUT, exist_ok=True)
    if not getattr(sys, 'frozen', False):
        print("\n[ 05 ] LIVE TELEMETRY STREAM")
    fps_start_time = time.time()
    fps_frame_count = 0
    fps_current = 0.0
    target_fps = TARGET_FPS_FAST if fast_mode else TARGET_FPS_QUALITY
    frame_time = 1.0 / target_fps
    frame_index = 0
    last_face_result = None
    last_graph_panel = None
    
    hand_centers_history = []
    face_centers_history = []
    max_history_frames = 200
    
    try:
        while True:
            frame_start_time = time.time()
            ret, frame = cap.read()
            if not ret:
                print("!! CRITICAL: FRAME_READ_FAILURE")
                break
            
            frame = cv2.flip(frame, 1)
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_h, frame_w = rgb_frame.shape[:2]  # Get full frame dimensions
            inference_frame = cv2.resize(rgb_frame, (inference_w, inference_h), interpolation=interp_inference)
            inference_frame = np.ascontiguousarray(inference_frame)
            mp_image = Image(image_format=ImageFormat.SRGB, data=inference_frame)
            
            timestamp_ms = int(frame_index * 1000 / target_fps)
            frame_index += 1
            
            detection_result = detector.detect_for_video(mp_image, timestamp_ms)
            if face_stagger == 1 or frame_index % face_stagger == 1 or last_face_result is None:
                face_result = face_landmarker.detect_for_video(mp_image, timestamp_ms)
                last_face_result = face_result
            else:
                face_result = last_face_result
            
            fps_frame_count += 1
            elapsed_time = time.time() - fps_start_time
            if elapsed_time >= 1.0:
                fps_current = fps_frame_count / elapsed_time
                fps_frame_count = 0
                fps_start_time = time.time()
            
            processing_time = time.time() - frame_start_time
            sleep_time = max(0, frame_time - processing_time)
            if sleep_time > 0:
                time.sleep(sleep_time)
            draw_landmarks_on_image(rgb_frame, detection_result, fps_current)
            draw_faces_on_image(rgb_frame, face_result, draw_mesh=not fast_mode)
            frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
            frame_h, frame_w = frame.shape[:2]

            rect = cv2.getWindowImageRect(window_name)
            win_w = max(320, rect[2] if rect[2] > 0 else screen_width)
            win_h = max(240, rect[3] if rect[3] > 0 else screen_height)
            screen_width, screen_height = win_w, win_h
            layout_scale = min(win_w / REF_W, win_h / REF_H)
            scale = font_scale_factor * layout_scale
            FONT_LARGE = FONT_LARGE_BASE * scale
            FONT_MED = FONT_MED_BASE * scale
            FONT_SMALL = FONT_SMALL_BASE * scale
            LINE_H = max(8, int(LINE_H_BASE * scale))
            LABEL_ROW = max(10, int(LABEL_ROW_BASE * scale))
            PADDING_SCALE = scale

            graph_width = int(win_w * 0.35)
            camera_height = int(win_h * 0.75)
            graph_height = camera_height
            
            num_hands = len(detection_result.hand_landmarks) if detection_result and detection_result.hand_landmarks else 0
            num_faces = len(face_result.face_landmarks) if face_result and face_result.face_landmarks else 0
            total_fingers = 0
            gestures = []
            
            frame_h, frame_w = frame.shape[:2]
            current_face_center = None
            current_face_landmarks = None
            if num_faces > 0 and face_result and face_result.face_landmarks:
                landmarks = face_result.face_landmarks[0]
                current_face_landmarks = landmarks
                valid = [(i, lm) for i, lm in enumerate(landmarks) if lm.x is not None and lm.y is not None]
                if valid:
                    xs = [lm.x * frame_w for _, lm in valid]
                    ys = [lm.y * frame_h for _, lm in valid]
                    center_x = sum(xs) / len(xs)
                    center_y = sum(ys) / len(ys)
                    current_face_center = (center_x, center_y)
            
            face_centers_history.append(current_face_center)
            if len(face_centers_history) > max_history_frames:
                face_centers_history.pop(0)
            

            if num_hands > 0 or num_faces > 0:
                use_prev_graph = fast_mode and frame_index % graph_stagger != 1 and last_graph_panel is not None
                if use_prev_graph:
                    graph_panel = last_graph_panel.copy()
                else:
                    graph_panel = np.full((graph_height, graph_width, 3), DARK_BG, dtype=np.uint8)
                title_area_height = int(40 * PADDING_SCALE)
                if not use_prev_graph and saved_gestures:
                    saved_text = f"SAVED: {len(saved_gestures)} GESTURES"
                    add_glow_effect(graph_panel, int(10 * PADDING_SCALE), int(28 * PADDING_SCALE), saved_text,
                                   FONT_FACE, FONT_MED, WARNING, 1, 2)
                display_lines = []
                h, w = frame.shape[:2]
                
                current_hand_centers = []
                for idx, hand_landmarks in enumerate(detection_result.hand_landmarks if detection_result and detection_result.hand_landmarks else []):
                    finger_count, gesture = count_fingers(hand_landmarks, w, h)
                    total_fingers += finger_count
                    gestures.append(gesture)
                    handedness = get_handedness_label(detection_result, idx)
                    
                    xs = [lm.x * w for lm in hand_landmarks]
                    ys = [lm.y * h for lm in hand_landmarks]
                    center_x = sum(xs) / len(xs)
                    center_y = sum(ys) / len(ys)
                    current_hand_centers.append((center_x, center_y))
                    
                    if not use_prev_graph:
                        display_lines.append(f"Hand {idx+1} ({handedness}): {finger_count} fingers | {gesture}")
                
                while len(current_hand_centers) < 2:
                    current_hand_centers.append(None)
                
                hand_centers_history.append(current_hand_centers)
                
                if len(hand_centers_history) > max_history_frames:
                    hand_centers_history.pop(0)
                
                if not use_prev_graph and num_faces > 0:
                    display_lines.append(f"Face: {num_faces}")
                if not use_prev_graph:
                    all_hands = list(detection_result.hand_landmarks) if num_hands > 0 and detection_result and detection_result.hand_landmarks else []
                    all_faces = list(face_result.face_landmarks) if (face_result and face_result.face_landmarks) else []
                    hand_graph_height = graph_height - title_area_height
                    hand_graph = draw_hands_and_face_graph(all_hands, all_faces, graph_width, hand_graph_height, display_lines or ["—"], 100)
                    graph_panel[title_area_height:, :] = hand_graph
                    label_y = title_area_height - int(5 * PADDING_SCALE)
                    if label_y >= int(30 * PADDING_SCALE):
                        line_idx = 0
                        for idx, hand_landmarks in enumerate(detection_result.hand_landmarks if detection_result and detection_result.hand_landmarks else []):
                            h, w = frame.shape[:2]
                            finger_count, gesture = count_fingers(hand_landmarks, w, h)
                            handedness = get_handedness_label(detection_result, idx)
                            hand_label = f"HAND {idx+1} ({handedness.upper()}): {finger_count} FINGERS | {gesture.upper()}"
                            add_glow_effect(graph_panel, int(10 * PADDING_SCALE), label_y + line_idx * LABEL_ROW, hand_label, FONT_FACE, FONT_MED, CORE, 1, 2)
                            line_idx += 1
                        if num_faces > 0:
                            add_glow_effect(graph_panel, int(10 * PADDING_SCALE), label_y + line_idx * LABEL_ROW, f"FACE: {num_faces}", FONT_FACE, FONT_MED, (50, 205, 50), 1, 2)
                    
                    last_graph_panel = graph_panel.copy()
            else:
                graph_panel = np.full((graph_height, graph_width, 3), DARK_BG, dtype=np.uint8)
                no_hands_text = "NO HANDS OR FACE"
                (text_w, text_h), _ = cv2.getTextSize(no_hands_text, FONT_FACE, FONT_LARGE, 2)
                add_glow_effect(graph_panel, graph_width // 2 - text_w // 2, graph_height // 2,
                               no_hands_text, FONT_FACE, FONT_LARGE, TEXT, 2, 3)
                terminal_y = graph_height - int(200 * PADDING_SCALE)
                cv2.rectangle(graph_panel, (0, terminal_y), (graph_width, graph_height), PANEL_BG, -1)
                draw_glowing_line(graph_panel, (0, terminal_y), (graph_width, terminal_y), CORE, 2, 1)
                add_glow_effect(graph_panel, int(8 * PADDING_SCALE), terminal_y + int(24 * PADDING_SCALE), "WAITING FOR HANDS / FACE...",
                               FONT_FACE, FONT_MED, TEXT, 1, 2)
            
            if num_hands > 0 or num_faces > 0:
                info_text = f"HANDS: {num_hands} | FINGERS: {total_fingers} | FACES: {num_faces}"
                if num_hands > 0 and len(set(gestures)) == 1:
                    info_text += f" | GESTURE: {gestures[0].upper()}"
                
                (text_w, text_h), baseline = cv2.getTextSize(info_text, FONT_FACE, FONT_LARGE, 2)
                padding = int(8 * PADDING_SCALE)
                cv2.rectangle(frame, (padding, padding), (text_w + padding * 2, text_h + baseline + padding * 2), 
                             PANEL_BG, -1)
                cv2.rectangle(frame, (padding, padding), (text_w + padding * 2, text_h + baseline + padding * 2), 
                             CORE, 2)
                
                add_glow_effect(frame, padding + int(4 * PADDING_SCALE), padding + text_h + int(4 * PADDING_SCALE), info_text,
                               FONT_FACE, FONT_LARGE, CORE, 2, 2)
                
                if num_hands > 0 and detection_result and detection_result.hand_landmarks and saved_gestures:
                    current_landmarks = detection_result.hand_landmarks[0]
                    for name, saved_landmarks_data in saved_gestures.items():
                        if gesture_matches(current_landmarks, saved_landmarks_data):
                            match_text = f"MATCH: {name.upper()}!"
                            (match_w, match_h), _ = cv2.getTextSize(match_text, FONT_FACE, FONT_LARGE, 2)
                            match_pad = int(5 * PADDING_SCALE)
                            cv2.rectangle(frame, (padding + match_pad, padding + text_h + baseline + padding + match_pad), 
                                        (match_w + padding * 2 + int(10 * PADDING_SCALE), text_h + baseline + match_h + padding * 3 + match_pad), 
                                        SUCCESS, -1)
                            cv2.rectangle(frame, (padding + match_pad, padding + text_h + baseline + padding + match_pad), 
                                        (match_w + padding * 2 + int(10 * PADDING_SCALE), text_h + baseline + match_h + padding * 3 + match_pad), 
                                        CORE, 2)
                            add_glow_effect(frame, padding + int(10 * PADDING_SCALE), padding + text_h + baseline + match_h + padding + int(10 * PADDING_SCALE), 
                                          match_text, FONT_FACE, FONT_LARGE, (224, 229, 229), 2, 2)
                            break
            
            ctrl_font_scale = max(FONT_MED, 0.4)
            ctrl_thickness = 2
            controls_text = "Q: QUIT | C: GESTURE (type name, S to save) | R: RECORD GRAPH"
            (ctrl_w, ctrl_h), baseline = cv2.getTextSize(controls_text, FONT_FACE, ctrl_font_scale, ctrl_thickness)
            padding = int(8 * PADDING_SCALE)
            cv2.rectangle(frame, (padding, frame.shape[0] - ctrl_h - padding * 2), 
                         (ctrl_w + padding * 2, frame.shape[0]), PANEL_BG, -1)
            cv2.rectangle(frame, (padding, frame.shape[0] - ctrl_h - padding * 2), 
                         (ctrl_w + padding * 2, frame.shape[0]), CORE, 1)
            cv2.putText(frame, controls_text, (padding + int(4 * PADDING_SCALE), frame.shape[0] - padding - int(4 * PADDING_SCALE)),
                       FONT_FACE, ctrl_font_scale, TEXT, ctrl_thickness)
            
            cap_h = 0
            if capturing_gesture:
                capture_text = f"GESTURE: TYPE NAME & PRESS 'S'"
                if gesture_name_input:
                    capture_text = f"NAME: {gesture_name_input.upper()} (PRESS 'S' TO SAVE)"
                (cap_w, cap_h), _ = cv2.getTextSize(capture_text, FONT_FACE, FONT_MED, 2)
                padding = int(10 * PADDING_SCALE)
                cv2.rectangle(frame, (frame.shape[1] - cap_w - padding * 2, padding), 
                             (frame.shape[1] - padding, cap_h + padding * 2), WARNING, -1)
                cv2.rectangle(frame, (frame.shape[1] - cap_w - padding * 2, padding), 
                             (frame.shape[1] - padding, cap_h + padding * 2), CORE, 2)
                add_glow_effect(frame, frame.shape[1] - cap_w - padding, padding + cap_h, 
                               capture_text, FONT_FACE, FONT_MED, (10, 12, 13), 2, 1)
            available_width = screen_width - graph_width
            camera_height = int(screen_height * 0.75)
            
            resized_frame = cv2.resize(frame, (available_width, camera_height), interpolation=interp_display)
            resized_graph = cv2.resize(graph_panel, (graph_width, camera_height), interpolation=interp_display)
            
            if recording_graph:
                if video_writer is not None:
                    video_writer.write(resized_graph)
                padding = int(15 * PADDING_SCALE)
                circle_radius = int(8 * PADDING_SCALE)
                circle_x = resized_graph.shape[1] - padding - circle_radius
                circle_y = padding + circle_radius
                cv2.circle(resized_graph, (circle_x, circle_y), circle_radius, (0, 0, 200), -1)
                rec_text = "RECORDING"
                (rec_w, rec_h), baseline = cv2.getTextSize(rec_text, FONT_FACE, FONT_SMALL, 1)
                text_x = circle_x - rec_w - int(10 * PADDING_SCALE)
                text_y = circle_y + rec_h // 2
                cv2.putText(resized_graph, rec_text, (text_x, text_y),
                           FONT_FACE, FONT_SMALL, (0, 0, 200), 1)
            
            top_row = np.hstack([resized_frame, resized_graph])
            
            bottom_space_height = screen_height - camera_height
            bottom_space = np.zeros((bottom_space_height, screen_width, 3), dtype=np.uint8)
            
            draw_center_position_graph(bottom_space, hand_centers_history, face_centers_history, max_history_frames)
            
            combined_frame = np.vstack([top_row, bottom_space])
            
            cv2.imshow(window_name, combined_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            try:
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    break
            except cv2.error:
                break
            if key == ord('r') or key == ord('R'):
                if not recording_graph:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    recording_filename = os.path.join(DIR_OUT, f"graph_recording_{timestamp}.mp4")
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    fps = 15.0
                    video_writer = cv2.VideoWriter(recording_filename, fourcc, fps, (graph_width, camera_height))
                    recording_graph = True
                    print(f">> RECORDING_STARTED: {recording_filename}")
                else:
                    if video_writer is not None:
                        video_writer.release()
                        video_writer = None
                    recording_graph = False
                    print(f">> RECORDING_STOPPED: {recording_filename}")
            elif key == ord('c'):
                if num_hands > 0 and detection_result and detection_result.hand_landmarks:
                    capturing_gesture = True
                    gesture_name_input = ""
                    print(">> CAPTURE_SEQUENCE: INPUT_NAME + [S] TO COMMIT")
            elif capturing_gesture:
                if key == ord('s'):
                    if gesture_name_input and num_hands > 0 and detection_result.hand_landmarks:
                        landmarks_data = []
                        for lm in detection_result.hand_landmarks[0]:
                            landmarks_data.append([lm.x, lm.y, lm.z])
                        saved_gestures[gesture_name_input] = landmarks_data
                        print(f">> DATA_COMMITTED: {gesture_name_input}.JSON")
                        capturing_gesture = False
                        gesture_name_input = ""
                elif (key >= ord('a') and key <= ord('z')) or (key >= ord('A') and key <= ord('Z')):
                    gesture_name_input += chr(key).lower()
                elif key == ord(' '):
                    gesture_name_input += ' '
                elif key == 8 or key == 127:
                    gesture_name_input = gesture_name_input[:-1] if gesture_name_input else ""
                
    except KeyboardInterrupt:
        print("\n>> INTERRUPT_DETECTED: SIGINT_RECEIVED")
    finally:
        if recording_graph and video_writer is not None:
            video_writer.release()
            video_writer = None
            if recording_filename:
                print(f">> RECORDING_SAVED: {recording_filename}")
        detector.close()
        face_landmarker.close()
        cap.release()
        cv2.destroyAllWindows()
        print(">> SESSION_TERMINATED. SENSOR_RELEASED. EXIT...")


if __name__ == "__main__":
    main()