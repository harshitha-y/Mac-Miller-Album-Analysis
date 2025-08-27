import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(
    page_title="Swimming in Circles",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Data Loading and Caching ---
@st.cache_data
def load_data(filepath):
    
    try:
        df = pd.read_csv(filepath)
        
        
        # Create a 'long' dataframe for bar chart and heatmap
        long_df = pd.melt(df, 
                          id_vars=['album', 'track_title'], 
                          value_vars=['song_emotion_1', 'song_emotion_2', 'song_emotion_3'],
                          var_name='emotion_slot',
                          value_name='emotion')
        
        long_scores_df = pd.melt(df, 
                                 id_vars=['album', 'track_title'], 
                                 value_vars=['song_score_1', 'song_score_2', 'song_score_3'],
                                 var_name='score_slot',
                                 value_name='score')
        
        long_df['score'] = long_scores_df['score']
        long_df = long_df.drop(columns=['emotion_slot'])
        
        # Return both the original 'wide' and the reshaped 'long' dataframes
        return df, long_df
    except FileNotFoundError:
        st.error(f"Error: '{filepath}' not found. Please make sure the file is in the correct directory.")
        return None, None


def main():
    st.title("Swimming in Circles: Mac Miller's Emotional Evolution")
    
    #intro
    col1, col2 = st.columns([3, 3])
    with col1:
        st.image("Streamlit-dashboard/image.png")
    with col2:
        st.markdown("""Mac Miller's music has always been a part of my playlist, very honest, authentic and metaphorical to me. Mac is the essence of what being human means, he would make you feel his music even if you can't fully relate. There was always a self aware undertone with him where he knows that everyone knows that being human is strange, thrilling, and impossible to truly put into words. I used to listen to ‘Good News’ as soon as I woke up for months as my everyday routine and every now and then I would realize more about his depressive state that was kinda masked in a calming song. It's brilliant to be able to do that. He was always known to be very open about his struggles and drug addiction in the interviews and his music, that vulnerability made his art resonate even more. This gave me an idea of how I could analyze his albums to actually see what emotions he was going through during three different years of his live when he made (not released) albums:

1. Balloonerism (2014)   : Peak addiction and drug usage
2. Swimming (2016)       : Attempting sobriety, trying to get out of addiction
3. Circles (2018)        : Gave into addiction

So, here are some results I got, after analysing lyrics in each song using Gemini LLM, that show different emotions he might’ve been feeling, reflected in his music, along with the overall emotional palette of his songs in the years leading up to his death. I hope you enjoy the analysis.

-Harshitha """)
    st.divider()


    df, long_df = load_data('Streamlit-dashboard/Analysed_data.csv')

    if long_df is not None and df is not None:
        
        # Sidebar for Album Selection 
        st.sidebar.header("Album Selection")
        album_list = long_df['album'].unique()
        selected_album = st.sidebar.selectbox(
            "Choose an album to view:",
            album_list
        )

        # Filter both dataframes for song scores
        album_data_long = long_df[long_df['album'] == selected_album]
        album_data_wide = df[df['album'] == selected_album].copy()
        album_data_wide['total_score'] = album_data_wide['song_score_1'] + album_data_wide['song_score_2'] + album_data_wide['song_score_3']

        
        # Calculate summary metrics
        most_frequent_emotion = album_data_long['emotion'].mode()[0]
        most_intense_song = album_data_wide.loc[album_data_wide['total_score'].idxmax()]['track_title']
        avg_intensity = album_data_long['score'].mean()
        
        
        

        #Album story
        
        if selected_album == 'Balloonerism':
            st.header(f"Album: *{selected_album}*")
            st.info('> "Yeah, somebody died today / I saw his picture in the funny papers / Didn’t think anybody died on a Friday" - *Funny Papers* (Haunting in hindsight, Mac passed away on a friday)')
            st.subheader(f"The Story")
            st.markdown("""
            Balloonerism feels like Mac at the height of his chaos. It’s raw, messy, and almost uncomfortable in how honest it is. The whole album drips with drug-fueled haze, late-night paranoia, and that unfiltered sadness that doesn’t even try to hide. Written almost only in a week back in 2014, at the height of his drug use, the album shows fear and anxiety that isn’t present in Swimming or Circles. You can hear nostalgia and longing woven through the lyrics, this constant sense of looking back to a time when life felt lighter, before the drugs took over. There’s a sadness in how much he misses that version of himself, even as he drowns deeper in substances.
            
            At the same time, Mac’s creative peak is on full display. He was exploding in fame, experimenting with sound, and pushing boundaries, but underneath all that artistry sits a deep depression. Balloonerism is both brilliant and tragic, the voice of someone wildly imaginative, but also completely consumed by addiction. It’s Mac at his most genius and most broken at the same time.""")
            
        elif selected_album == 'Swimming':
            st.header(f"Album: *{selected_album}*")
            st.info('> "And I was drownin\' but now I\'m swimmin\' Through stressful waters to relief." - *Come Back to Earth*')
            st.subheader(f"The Story")
            st.markdown("""A journey of learning to "swim" through depression
            
Swimming to me feels like Mac trying to figure out how to keep moving through depression instead of just letting it drown him. Around then, he managed to stay sober for a few months, and you can kinda hear that fight in the music. It’s not about celebrating being clean, it’s about how hard it is to actually do it. Compared to Balloonerism, which was just heavy with sadness and grief, Swimming feels more complicated. There’s this deep melancholy, and also a lot of frustration, almost like he’s mad at the addiction and what it’s taken from him. But the big difference is he’s not just giving in anymore but he’s processing it, learning to “swim” through his depression to get to a better place. It’s less about finally being okay and more about proving to himself that he can keep going.
        
'The ever-going motif throughout the album of self love being important, tracks supporting these theories are ‘Self Care’, ‘Ladders’ expressing the acceptance of his flaws, ‘What’s The Use’ showing how though his drug abuse is unhealthy, but it is something that he enjoys, and to shorten the list ‘Hurt Feelings’ in where he is put in a high throne looking down at the people that make part of his everyday life.' - *Genius*""")
            
        elif selected_album == 'Circles':
            st.header(f"Album: *{selected_album}*")
            st.info('> "I just end up right at the start of the line, drawing circles." - *Circles*')
            st.subheader(f"The Story")
            st.markdown("""
            *Circles* Circles was supposed to be the sister album of swimming. It feels like the other side of swimming where Mac stopped fighting and accepted his addiction. It’s way softer, more resigned and he’s tired. Tired of trying and showing the world he’s okay. A quiet acceptance that maybe the pain doesn’t go away, it just becomes a part of life. It’s reflective, almost meditative at times, but also heavy because you can sense he’s letting go of control. It’s not about beating depression, it’s about living inside it and trying to find peace within.
            
            "Circles" has metaphors for the cycle that he can't seem to break, "Good News” honestly shows Mac is aware of his situation while also feeling powerless to change it, “Hand Me Downs”  feels like one of the most intimate moments where Mac opens up about wanting love, stability, and someone to share life with despite his struggles.""")
            

        st.divider()

        
        
        
        # album stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Most Frequent Emotion", most_frequent_emotion)
        with col2:
            st.metric("Most Intense Song", most_intense_song)
        with col3:
            st.metric("Average Emotion Score", f"{avg_intensity:.2f}")
        
        st.divider()

        # --- 1. Bar Chart Display ---
        
        fig_bar = px.bar(
            album_data_long,
            x='track_title',
            y='score',
            color='emotion',
            barmode='group',
            title=f'Emotion Scores for Each Song in "{selected_album}" - Bar chart',
            labels={
                'track_title': 'Song Title',
                'score': 'Emotion Score',
                'emotion': 'Emotion'
            },
            height=600
        )
        fig_bar.update_layout(
            xaxis={'categoryorder':'total descending'},
            legend_title_text='Emotions'
        )
        fig_bar.update_xaxes(tickangle=45)
        st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()

        if selected_album == 'Balloonerism':
            st.info('> "I gave my life to this shit, already killed myself" - *Do You Have a Destination*')
        elif selected_album == 'Swimming':
            st.info('> "I just need a way out of my head / I’ll do anything for a way out of my head" - *Come Back to Earth*')
        elif selected_album == 'Circles':
            st.info('> "Wake up to the moon/ haven’t seen the sun in a while but I heard that the sky is still blue" - *Good News*')

        # --- 2. Polar Bar Chart for Total Intensity per Emotion ---
        
        emotion_intensity = album_data_long.groupby('emotion')['score'].sum().reset_index()

        fig_polar = px.bar_polar(
            emotion_intensity,
            r="score",
            theta="emotion",
            color="emotion",
            title=f'Total Intensity for Each Emotion in "{selected_album}" - Polar bar chart',
            labels={'emotion': 'Emotion', 'score': 'Total Score'},
            template="plotly_dark",
            color_discrete_sequence=px.colors.sequential.Plasma_r
        )
        fig_polar.update_layout(height=700)
        st.plotly_chart(fig_polar, use_container_width=True)


        st.divider()
        if selected_album == 'Balloonerism':
            st.info('> "Me, I used to want to be a wizard, when did life get so serious?" - *Excelsior*')
        elif selected_album == 'Swimming':
            st.info('> "You never told me being rich was so lonely\ Nobody know me, oh well\ Hard to complain from this five-star hotel" - *Small Worlds*')
        elif selected_album == 'Circles':
            st.info('> "There\'s a whole lot more for me waiting on the other side\ I\'m always wondering if it feel like summer" - *Good News*')

        # --- 3. Heatmap Display ---
       
        
        all_emotions_ordered = sorted(long_df['emotion'].unique())
        
        heatmap_pivot = album_data_long.pivot_table(
            index='track_title', 
            columns='emotion', 
            values='score'
        ).fillna(0)

        heatmap_pivot = heatmap_pivot.reindex(columns=all_emotions_ordered, fill_value=0)

        
        custom_purple_gradient = ['#EADADA', '#D59CC5', '#BE5CA9', '#4D3A4D']

        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=heatmap_pivot.values,
            x=heatmap_pivot.columns,
            y=heatmap_pivot.index,
            colorscale=custom_purple_gradient,
            text=heatmap_pivot.values,
            texttemplate="%{z:.2f}"
        ))

        fig_heatmap.update_layout(
            title_text=f'Emotion Intensities for "{selected_album}" - Heat map',
            title_x=0,
            height=750,
            width=900 
        )
        
        st.plotly_chart(fig_heatmap)

        st.divider()

        
        if selected_album == 'Balloonerism':
            st.info('> "You wonder when God will just listen and give you a break / And He says, ‘See, living and dying are one and the same‘ " - *Tomorrow Will Never Know*')
        elif selected_album == 'Swimming':
            st.info('> "Used to be feeling depressed/ Now that I\'m living and I\'m feeling obsessed" - *Hurt Feelings*')
        elif selected_album == 'Circles':
            st.info('> "But what\'s new? You get used to the bullshit, the screws, they go missin\' \ It\'s likely they might be, but...' \
            'You remind me, ' \
            'Shit, I need to stay in line \ You damn well are a great design" - *Hand me downs*')


        # --- 4. Emotion Spotlight Chart ---
    
        st.markdown("**Emotion Spotlight - Bar Plot**.")

        
        top_emotions_list = long_df['emotion'].value_counts().nlargest(10).index.tolist()
        selected_emotion = st.selectbox(
            "Select an emotion to spotlight:",
            top_emotions_list
        )

        if selected_emotion:
            
            scores = []
            for _, row in df.iterrows():
                score = 0
                if row['song_emotion_1'] == selected_emotion:
                    score = row['song_score_1']
                elif row['song_emotion_2'] == selected_emotion:
                    score = row['song_score_2']
                elif row['song_emotion_3'] == selected_emotion:
                    score = row['song_score_3']
                scores.append(score)

            # Create a temporary dataframe for plotting
            spotlight_df = df[['track_title', 'album']].copy()
            spotlight_df['score'] = scores

            # Create the bar chart
            fig_spotlight = px.bar(
                spotlight_df,
                x='track_title',
                y='score',
                color='album', # Color bars by album for better visual grouping
                title=f'Scores for Emotion: "{selected_emotion}" Across All Songs',
                labels={'track_title': 'Song Title', 'score': 'Emotion Score'}
            )

            # Add vertical lines to denote album changes
            album_end_indices = df.groupby('album').size().cumsum().values - 0.5
            for x_pos in album_end_indices[:-1]: # Exclude the last one
                fig_spotlight.add_vline(
                    x=x_pos, 
                    line_width=2, 
                    line_dash="dash", 
                    line_color="grey"
                )
            
            fig_spotlight.update_layout(height=600)
            fig_spotlight.update_xaxes(tickangle=90)

            st.plotly_chart(fig_spotlight, use_container_width=True)


if __name__ == "__main__":
    main()
