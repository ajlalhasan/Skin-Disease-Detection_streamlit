import streamlit as st
from database import get_db_connection
import pandas as pd

def show_admin_panel():
    """Main admin panel dashboard"""
    st.title("👤 Admin Panel")
    
    # Statistics overview
    show_statistics()
    
    st.write("---")
    
    # Quick actions
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👥 Manage Users", use_container_width=True):
            st.session_state.admin_page = "users"
            st.rerun()
    
    with col2:
        if st.button("👨‍⚕️ Manage Doctors", use_container_width=True):
            st.session_state.admin_page = "doctors"
            st.rerun()
    
    with col3:
        if st.button("💬 View Feedback", use_container_width=True):
            st.session_state.admin_page = "feedback"
            st.rerun()
    
    st.write("---")
    
    # Recent activity
    show_recent_activity()

def show_statistics():
    """Show system statistics"""
    st.subheader("📊 System Statistics")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get various statistics
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 0")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM doctors")
    total_doctors = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM predictions")
    total_predictions = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM feedback")
    total_feedback = cursor.fetchone()[0]
    
    # Display in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", total_users)
    
    with col2:
        st.metric("Total Doctors", total_doctors)
    
    with col3:
        st.metric("Total Predictions", total_predictions)
    
    with col4:
        st.metric("Feedback Received", total_feedback)
    
    # Disease prediction statistics
    cursor.execute('''
        SELECT predicted_disease, COUNT(*) as count 
        FROM predictions 
        GROUP BY predicted_disease 
        ORDER BY count DESC
    ''')
    
    disease_stats = cursor.fetchall()
    
    if disease_stats:
        st.subheader("Most Common Predictions")
        disease_df = pd.DataFrame(disease_stats, columns=['Disease', 'Count'])
        st.bar_chart(disease_df.set_index('Disease'))
    
    conn.close()

def show_recent_activity():
    """Show recent system activity"""
    st.subheader("📋 Recent Activity")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Recent predictions
    cursor.execute('''
        SELECT u.username, p.predicted_disease, p.confidence_score, p.created_at
        FROM predictions p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
        LIMIT 10
    ''')
    
    recent_predictions = cursor.fetchall()
    
    if recent_predictions:
        st.write("**Recent Predictions:**")
        for pred in recent_predictions:
            st.write(f"• {pred[0]} - {pred[1]} ({pred[2]:.2%} confidence) - {pred[3][:19]}")
    
    st.write("---")
    
    # Recent feedback
    cursor.execute('''
        SELECT u.username, f.rating, f.comments, f.created_at
        FROM feedback f
        JOIN users u ON f.user_id = u.id
        ORDER BY f.created_at DESC
        LIMIT 5
    ''')
    
    recent_feedback = cursor.fetchall()
    
    if recent_feedback:
        st.write("**Recent Feedback:**")
        for feedback in recent_feedback:
            comment = feedback[2][:50] + "..." if len(feedback[2]) > 50 else feedback[2]
            st.write(f"• {feedback[0]} - {feedback[1]}/5 stars: \"{comment}\" - {feedback[3][:19]}")
    
    conn.close()
