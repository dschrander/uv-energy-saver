import streamlit as st
import pandas as pd
from flexo_uv_curing import FlexoUVCuring
from utils import validate_bcm, load_saved_settings, save_settings, get_help_text
from styles import apply_custom_styles

def main():
    # Apply custom styling
    apply_custom_styles()

    # Initialize session state
    if 'saved_settings' not in st.session_state:
        st.session_state.saved_settings = load_saved_settings()

    # Initialize FlexoUVCuring instance
    uv_curing = FlexoUVCuring()

    # Header
    st.markdown('<div class="industrial-header">', unsafe_allow_html=True)
    st.title("CleverCuring - UV Calculator")
    st.markdown('</div>', unsafe_allow_html=True)

    # Help information
    with st.expander("ℹ️ Help & Informatie"):
        st.markdown(get_help_text('general'))

    # Main input form
    with st.form("uv_settings_form"):
        col1, col2 = st.columns(2)

        with col1:
            substraat = st.selectbox(
                "Substraat Type",
                options=['Gecoat papier', 'Ongecoat papier', 'Folie', 'Karton'],
                help=get_help_text('substrate')
            )

            inktsoort = st.selectbox(
                "Inktsoort",
                options=['UV-inkt', 'Watergedragen inkt', 'LED-UV inkt'],
                help=get_help_text('ink_type')
            )

        with col2:
            rasterwals_type = st.selectbox(
                "Rasterwals Type",
                options=[
                    'Hexagonal (20-30% transfer)',
                    'Hachure / Trihelical (35-40% transfer)',
                    'ART / TIF (40-50% transfer)',
                    'GTT UniCoat (25-30% transfer)'
                ],
                help=get_help_text('rasterwals')
            )

            # Get volume specifications for selected rasterwals type
            volume_specs = uv_curing.get_volume_specs(rasterwals_type)
            volume_options = [spec['volume'] for spec in volume_specs]

            selected_volume = st.selectbox(
                "Rasterwals Volume",
                options=volume_options,
                help=get_help_text('volume')
            )

            # Get BCM value for selected volume
            bcm = uv_curing.get_bcm_from_volume(rasterwals_type, selected_volume)

            # Display additional information
            spec_info = next((spec for spec in volume_specs if spec['volume'] == selected_volume), None)
            if spec_info:
                info_text = f"""
                Specificaties:
                - Volume: {spec_info.get('actual_volume', spec_info['volume'])}
                - BCM: {spec_info['bcm']}
                - Lijnen: {spec_info['lines']}
                - Inktoverdracht: {spec_info['transfer']}
                """
                st.info(info_text)

        calculate_button = st.form_submit_button("Bereken UV Vermogen")

    # Calculate and display results
    if calculate_button:
        if not validate_bcm(bcm):
            st.error("BCM waarde moet tussen 0 en 20 liggen.")
        else:
            result = uv_curing.bereken_uv_vermogen(substraat, inktsoort, bcm, rasterwals_type, selected_volume)

            # Display results in an organized way
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.subheader("Berekende UV Instellingen")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("UV Vermogen", f"{result['final_power']}%")
            with col2:
                st.metric("Inktoverdracht", result['transfer_value'])

            # Detailed breakdown
            st.markdown("### Berekening Details")
            st.write(f"Basisvermogen: {result['base_power']}%")
            st.write(f"Substraat aanpassing: {result['substrate_contribution']:.1f}%")
            st.write(f"Inkt aanpassing: {result['ink_contribution']:.1f}%")
            st.write(f"Rasterwals: {rasterwals_type}")
            st.write(f"Volume: {selected_volume}")
            st.write(f"Transfer factor: {result['transfer_factor']:.1f}%")
            st.markdown('</div>', unsafe_allow_html=True)

            # Save settings option
            if st.button("Instellingen Opslaan"):
                new_setting = {
                    "substraat": substraat,
                    "inktsoort": inktsoort,
                    "rasterwals_type": rasterwals_type,
                    "volume": selected_volume,
                    "bcm": bcm,
                    "vermogen": result['final_power'],
                    "transfer": result['transfer_value']
                }
                st.session_state.saved_settings.append(new_setting)
                save_settings(st.session_state.saved_settings)
                st.success("Instellingen opgeslagen!")

    # Display saved settings
    if st.session_state.saved_settings:
        st.markdown("### Opgeslagen Instellingen")
        df = pd.DataFrame(st.session_state.saved_settings)
        st.dataframe(df)

if __name__ == "__main__":
    main()
