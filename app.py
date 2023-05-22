import colorsys

import streamlit as st

import fragments
import util
from util import ThemeColor


preset_colors: list[tuple[str, ThemeColor]] = [
    ("Default light", ThemeColor(
            primaryColor="#ff4b4b",
            backgroundColor="#ffffff",
            secondaryBackgroundColor="#f0f2f6",
            textColor="#31333F",
        )),
    ("Default dark", ThemeColor(
            primaryColor="#ff4b4b",
            backgroundColor="#0e1117",
            secondaryBackgroundColor="#262730",
            textColor="#fafafa",
    ))
]

theme_from_initial_config = util.get_config_theme_color()
if theme_from_initial_config:
    preset_colors.append(("From the config", theme_from_initial_config))

default_color = preset_colors[0][1]


def sync_rgb_to_hls(key: str):
    # HLS states are necessary for the HLS sliders.
    rgb = util.parse_hex(st.session_state[key])
    hls = colorsys.rgb_to_hls(rgb[0], rgb[1], rgb[2])
    st.session_state[f"{key}H"] = round(hls[0] * 360)
    st.session_state[f"{key}L"] = round(hls[1] * 100)
    st.session_state[f"{key}S"] = round(hls[2] * 100)


def sync_hls_to_rgb(key: str):
    h = st.session_state[f"{key}H"]
    l = st.session_state[f"{key}L"]
    s = st.session_state[f"{key}S"]
    r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    st.session_state[key] = f"#{round(r * 255):02x}{round(g * 255):02x}{round(b * 255):02x}"


def set_color(key: str, color: str):
    st.session_state[key] = color
    sync_rgb_to_hls(key)


if 'preset_color' not in st.session_state or 'backgroundColor' not in st.session_state or 'secondaryBackgroundColor' not in st.session_state or 'textColor' not in st.session_state:
    set_color('primaryColor', default_color.primaryColor)
    set_color('backgroundColor', default_color.backgroundColor)
    set_color('secondaryBackgroundColor', default_color.secondaryBackgroundColor)
    set_color('textColor', default_color.textColor)


st.title("UI Page")


def on_preset_color_selected():
    _, color = preset_colors[st.session_state.preset_color]
    set_color('primaryColor', color.primaryColor)
    set_color('backgroundColor', color.backgroundColor)
    set_color('secondaryBackgroundColor', color.secondaryBackgroundColor)
    set_color('textColor', color.textColor)


st.selectbox("Preset colors", key="preset_color", options=range(len(preset_colors)), format_func=lambda idx: preset_colors[idx][0], on_change=on_preset_color_selected)

if st.button("🎨🥝 Generate a random color scheme 🎲"):
    primary_color, text_color, basic_background, secondary_background = util.generate_color_scheme()
    set_color('primaryColor', primary_color)
    set_color('backgroundColor', basic_background)
    set_color('secondaryBackgroundColor', secondary_background)
    set_color('textColor', text_color)


def color_picker(label: str, key: str, default_color: str, l_only: bool) -> None:
    col1, col2 = st.columns([1, 3])
    with col1:
        color = st.color_picker(label, key=key, on_change=sync_rgb_to_hls, kwargs={"key": key})
    with col2:
        r,g,b = util.parse_hex(default_color)
        h,l,s = colorsys.rgb_to_hls(r,g,b)
        if l_only:
            if f"{key}H" not in st.session_state:
                st.session_state[f"{key}H"] = round(h * 360)
        else:
            st.slider(f"H for {label}", key=f"{key}H", min_value=0, max_value=360, value=round(h * 360), format="%d°", label_visibility="collapsed", on_change=sync_hls_to_rgb, kwargs={"key": key})

        st.slider(f"L for {label}", key=f"{key}L", min_value=0, max_value=100, value=round(l * 100), format="%d%%", label_visibility="collapsed", on_change=sync_hls_to_rgb, kwargs={"key": key})

        if l_only:
            if f"{key}S" not in st.session_state:
                st.session_state[f"{key}S"] = round(s * 100)
        else:
            st.slider(f"S for {label}", key=f"{key}S", min_value=0, max_value=100, value=round(s * 100), format="%d%%", label_visibility="collapsed", on_change=sync_hls_to_rgb, kwargs={"key": key})

    return color


primary_color = color_picker('Primary color', key="primaryColor", default_color=default_color.primaryColor, l_only=True)
text_color = color_picker('Text color', key="textColor", default_color=default_color.textColor, l_only=True)
background_color = color_picker('Background color', key="backgroundColor", default_color=default_color.backgroundColor, l_only=True)
secondary_background_color = color_picker('Secondary background color', key="secondaryBackgroundColor", default_color=default_color.secondaryBackgroundColor, l_only=True)


st.header("WCAG contrast ratio")
st.markdown("""
Check if the color contrasts of the selected colors are enough to the WCAG guidelines recommendation.

def synced_color_picker(label: str, value: str, key: str):
    def on_change():
        st.session_state[key] = st.session_state[key + "2"]
        sync_rgb_to_hls(key)
    st.color_picker(label, value=value, key=key + "2", on_change=on_change)

col1, col2, col3 = st.columns(3)
with col2:
    synced_color_picker("Background color", value=background_color, key="backgroundColor")
with col3:
    synced_color_picker("Secondary background color", value=secondary_background_color, key="secondaryBackgroundColor")

col1, col2, col3 = st.columns(3)
with col1:
    synced_color_picker("Primary color", value=primary_color, key="primaryColor")
with col2:
    fragments.contrast_summary("Primary/Background", primary_color, background_color)
with col3:
    fragments.contrast_summary("Primary/Secondary background", primary_color, secondary_background_color)

col1, col2, col3 = st.columns(3)
with col1:
    synced_color_picker("Text color", value=text_color, key="textColor")
with col2:
    fragments.contrast_summary("Text/Background", text_color, background_color)
with col3:
    fragments.contrast_summary("Text/Secondary background", text_color, secondary_background_color)


st.header("Config")

st.subheader("Config file (`.streamlit/config.toml`)")
st.code(f"""
[theme]
primaryColor="{primary_color}"
backgroundColor="{background_color}"
secondaryBackgroundColor="{secondary_background_color}"
textColor="{text_color}"
""", language="toml")

st.subheader("Command line argument")
st.code(f"""
streamlit run app.py \\
    --theme.primaryColor="{primary_color}" \\
    --theme.backgroundColor="{background_color}" \\
    --theme.secondaryBackgroundColor="{secondary_background_color}" \\
    --theme.textColor="{text_color}"
""")


if st.checkbox("🥝Apply theme to this page"):
    st.info("Select 'Custom Theme' in the settings dialog to see the effect")

    def reconcile_theme_config():
        keys = ['primaryColor', 'backgroundColor', 'secondaryBackgroundColor', 'textColor']
        has_changed = False
        for key in keys:
            if st._config.get_option(f'theme.{key}') != st.session_state[key]:
                st._config.set_option(f'theme.{key}', st.session_state[key])
                has_changed = True
        if has_changed:
            st.experimental_rerun()

    reconcile_theme_config()

    fragments.sample_components("body")
    with st.sidebar:
        fragments.sample_components("sidebar")


        
        
        
        
        
        
        
        
        
        
        
        
        

st.markdown("""
# 🥝Introduce
Language : English \n
Fascinating tool to Make the UI more beautiful! \n 
open-map

# 🥝Basic functions

## color
Set your theme colors.  \n   
We can keep trying, and page colors can create many possibilities, just if we want to.\n
Let's go on.✨
  


## how to use UI
First,Click box🍇（Apply theme to this page.）\n 
Then click the button ( Generate a random color scheme 🎲)


Click the button again , move the slider again , then select a theme to read. \n 

Now you can create the UI theme you want.
It is a slider that can be adjusted in increments of 0.01.
The higher the number, the stronger the brightness of the color. \n 

Free to explore.

## custom 
You can create your own Color theme. \n   
Why not read  article on a color that makes you feel comfortable?🧸

### example
Reading a good book， like and many noble people talk.  (Goethe)  \n 
Who to idle away one's time， youth will Ken color， life will abandon them. (Hugo) \n 
The real agile is a valuable thing.  (Bacon)








# 🥝Models
In the design of machine learning models,  
researchers need to consider factors such as the quality and quantity of data,
the complexity and efficiency of algorithms,
and the interpretability of models.


## for example
🔭In the field of natural language processing,
   researchers have developed a variety of language models,
   including bag-of-words models, recurrent neural networks (RNN),
   and transformer models, among others.
🔭The design of these models needs to take into account the structure and laws of the language,
   as well as the distribution of data and the size of the sample.



# 🥝View
🤓The beauty of machine learning refers to the process of realizing technological innovation 
   and artistic creation through machine learning technology.   \n 
🤓With the development of artificial intelligence technology in recent years,
   the beauty of machine learning has gradually become a hot topic.   \n 
🤓The beauty of machine learning can be applied in many fields,
   such as music creation, machine painting, film and television production, etc.   \n 
🤓Through the analysis and learning of machine learning algorithms,
   computers can automatically generate artwork or art reviews.   \n 
🤓so as to achieve certain artistic effects.




## code art
The aesthetics of machine learning code refers to aspects, 
such as code readability, simplicity, modularity, and portability.


### comment of code
In addition, code comments are also very important.


### part 1
Comments should clearly explain what the code does and how it is implemented 
so that others can understand and modify the code.

### part 2
In short, the code aesthetics of machine learning is to consider the readability,
simplicity, modularity and portability of the code while implementing the machine learning algorithm,
so that others can easily understand and modify the code,
and finally achieve a beautiful functions and services.


# 🥝Decision support
Traditional data labeling methods require manual processing and analysis,
while machine learning can automate this process,
quickly find out some laws and patterns,
nd perform prediction and decision support.


## for example
🧑‍⚕️In the medical field,
   machine learning can assist doctors in disease diagnosis and treatment options,
   and improve patient outcomes.



# 🥝Aesthetic project

🍉Machine learning aesthetics will also have a positive impact on
  cultural heritage protection and digital inheritance. \n 
🍉Through machine learning algorithms,
   we can digitally restore and repair artworks in cultural heritage,
   thereby protecting and inheriting the precious cultural heritage of mankind. \n 
🍉For example, the digital mural project of Dunhuang Mogao Grottoes,
   the digital museum project, etc. \n 

## welcome

The future story should be awesome, so we welcome everyone to join👐

""")        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
     
