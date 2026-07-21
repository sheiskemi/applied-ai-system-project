# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

This recommender is designed to suggest songs based on a user's preferred genre, mood, and energy level. It assumes that users have clear music preferences and that songs with similar characteristics are more likely to be enjoyable. This project is intended for classroom learning to demonstrate how a simple **content-based** recommendation system works.

### Non-Intended Use

This recommender should not be used as a real music streaming recommendation engine. It does not learn from user listening history, adapt over time, or consider factors such as popularity, playlists, or user behavior. Because the dataset is small and the scoring logic is simple, it cannot provide highly personalized recommendations.

---

## 3. How the Model Works

The recommender compares each song in the catalog with the user's preferences. It looks at the song's genre, mood, and energy level. Songs that match the user's preferred genre receive the highest number of points, followed by songs that match the preferred mood. It also compares the song's energy level with the user's target energy and gives higher scores to songs that are closer. After every song is scored, the songs are sorted from the highest score to the lowest, and the top recommendations are returned with a short explanation of why they were selected.

---

## 4. Data

The dataset contains 18 songs from a variety of genres, including pop, lofi, rock, jazz, ambient, synthwave, **hip-hop**, classical, blues, folk, R&B, EDM, metal, and indie pop. Each song includes information such as genre, mood, energy, tempo, valence, danceability, and acousticness. Additional songs were added to make the dataset more diverse. Although the dataset covers several genres, it is still small and cannot represent the full variety of musical tastes.

---

## 5. Strengths

The recommender performs well when users have clear preferences for genre, mood, and energy. During testing, the High Energy Pop profile correctly recommended songs like *Sunrise City* and *Gym Hero*. The Chill Lofi profile also produced appropriate recommendations such as *Library Rain* and *Midnight Coding*. These results matched expectations and showed that the scoring system can identify songs with similar characteristics.

---

## 6. Limitations and Bias

The recommender only considers genre, mood, and energy when calculating recommendations. It ignores other useful features such as tempo, danceability, valence, and acousticness. Because the dataset contains only 18 songs, some recommendations appear repeatedly across different user profiles. The algorithm also requires exact genre and mood matches, which may overlook songs that have a similar style but different labels.

---

## 7. Evaluation

The recommender was tested using four different user profiles: High Energy Pop, Chill Lofi, Deep Intense Rock, and an edge case for a Happy Classical Fan. The recommendations generally matched the expected listening styles for each profile. The High Energy Pop profile favored upbeat pop songs, while the Chill Lofi profile recommended slower and more relaxing tracks. The Deep Intense Rock profile correctly ranked *Storm Runner* first because it matched both the preferred genre and mood. The edge case showed that when no song perfectly matched every preference, the recommender selected the closest available songs based on the scoring rules.

For comparison, the High Energy Pop profile focused on energetic pop songs, while the Chill Lofi profile shifted toward calm, low energy music. The Deep Intense Rock profile recommended heavier and more intense songs, which demonstrated that changing the user preferences changed the recommendations in a meaningful way.

I also tested how changing the scoring weights affected the recommendations. I reduced the genre weight from 2.0 to 1.0 and doubled the importance of energy. After making this change, songs with energy levels closer to the user's preference moved higher in the rankings, even when they were from a different genre. This showed that the weighting of each feature has a direct impact on the final rankings. Giving more importance to energy caused songs with similar energy levels to rank higher, even when they did not match the preferred genre.

---

## 8. Future Work

In the future, I would include more song features such as danceability, tempo, acousticness, and valence when calculating scores. I would also expand the dataset with hundreds or thousands of songs to improve recommendation quality. Another improvement would be to increase the diversity of recommendations so the same songs do not appear frequently across different user profiles. Finally, I would improve the explanation feature by showing exactly how each score was calculated.

---

## 9. Personal Reflection

This project helped me understand how recommendation systems compare user preferences with item features to generate personalized suggestions. My biggest learning moment was seeing how changing the scoring weights affected the recommendations, even with a simple algorithm. AI tools helped me generate ideas, debug my code, and understand different approaches, but I still needed to test the code and verify that the recommendations made sense. I was surprised that such a simple scoring system could produce recommendations that felt relevant to different user profiles. If I continued this project, I would expand the dataset, include more song features, and experiment with more advanced recommendation techniques.