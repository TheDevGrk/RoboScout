from multiprocessing.pool import ThreadPool
import data
import streamlit as st
import json

pool = ThreadPool(processes=2)

data.refreshData()

file = open("teamInfo.txt", "r")
teamInfo = json.loads(file.read())

st.button("Refresh")
st.write(teamInfo)