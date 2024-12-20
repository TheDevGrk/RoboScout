from multiprocessing.pool import ThreadPool
import data
import streamlit as st
import streamlit_modal as modal
import json
import time


pool = ThreadPool(processes=2)


pool.apply_async(data.refreshData)

file = open("teamInfo.txt", "r")
teamInfo = json.loads(file.read())
file.close()

st.write(teamInfo)