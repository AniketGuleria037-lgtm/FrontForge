import streamlit as st
import sys
import os
import zipfile
import io
sys.path.append(".")

from pipeline import build_pipeline
from main import write_files, write_package_json, ensure_config_files, fix_imports, npm_install, npm_build
from pathlib import Path
OUTPUT_DIR=Path("generated-app")

st.title("⚡ FrontForge AI")
st.write("Generate complete React applications from natural language — locally, no cloud, no API keys.")
st.divider()
prompt = st.text_area(
    "Describe the React app you want to build:",
    placeholder="Build a landing page for a coffee shop with menu, hero section and contact form",
    height=100
)
col1, col2, col3 = st.columns(3)
with col1:
    framework = st.selectbox("Framework", ["React", "Next.js"], index=0)
with col2:
    styling = st.selectbox("Styling", ["Tailwind", "Bootstrap"], index=0)
with col3:
    theme = st.selectbox("Theme", ["light", "dark"], index=0)

st.write("")
col1, col2, col3 = st.columns([1,1,1])
with col2:
    generate = st.button("⚡ Generate App", use_container_width=True)

if generate and prompt:
    st.divider()
    with st.status("Running FrontForge AI Pipeline...", expanded=True) as status:
        try:
            st.write("🔨 Building pipeline...")
            pipeline = build_pipeline()
            st.write("✅ Pipeline ready")
            st.write("🤖 Running agents — this takes 10-20 minutes...")

            initial_state = {
                "user_prompt": prompt,
                "specs": {
                    "framework": framework,
                    "styling": styling,
                    "theme": theme,
                    "pages": [],
                    "complexity": "simple"
                },
                "plan": None,
                "ui_architecture": None,
                "components": None,
                "style": None,
                "package": None,
                "review": None
            }

            final_state = pipeline.invoke(initial_state)
            st.write("✅ All agents completed")
            st.write("📁 Writing files...")

            review = final_state.get("review")
            style = final_state.get("style")

            if review and review.get("fixed_files") and len(review["fixed_files"]) > 2:
                files_data = {"files": review["fixed_files"]}
            elif style and style.get("files"):
                files_data = {"files": style["files"]}
            else:
                files_data = {"files": []}

            write_files(files_data)
            write_package_json(final_state.get("package", {}))
            ensure_config_files()
            fix_imports()

            st.write("📦 Running npm install...")
            npm_install()

            st.write("🔨 Building React app...")
            build_ok, error = npm_build()
            if build_ok:
                status.update(label="✅ Generation Complete!", state="complete")
                st.success("🎉 Your React app was generated successfully!")
                st.balloons()
    # Create zip for download
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for file_path in OUTPUT_DIR.rglob("*"):
                        if file_path.is_file():
                            if "node_modules" not in str(file_path):
                                zip_file.write(
                                    file_path,
                                    file_path.relative_to(OUTPUT_DIR)
                                )
                zip_buffer.seek(0)
    
                st.download_button(
                    label="⬇️ Download Generated App",
                    data=zip_buffer,
                    file_name="frontforge-app.zip",
                    mime="application/zip"
                )
                st.info("To preview: extract zip → npm install → npm run dev")

            else:
                status.update(label="⚠️ Build errors", state="error")
                st.error(f"Build error: {error[:500]}")
            
        except Exception as e:
            status.update(label="❌ Failed", state="error")
            st.error(f"Error: {str(e)}")
            

elif generate and not prompt:
    st.warning("Please enter a prompt first!")
