# Building a Dialogue Classification System for Human-Robot Interactions

## Authors
Ekele Ogbadu & Zach Margulies 

## Overview

Our work revolves around understanding and making use of the SCOUT (Situated Corpus of Understanding Transactions) data, a corpus of human-robot dialogue for an Urban Search & Rescue scenario. In this dataset, a human "commander" gives instructions to a robot that is navigating an urban setting. We have conducted an extensive user study in which participants were asked to select the most appropriate robot action in response to a human instruction (sampled from the SCOUT data). We determined the classification accuracy of participant-selected robot actions compared to the corresponding real output performed by the robot. Then, using a random forest classifier we built a system to translate the human commands into robot actions. Treating the user study as a baseline, we evaluated the performance of our new classifier. In future studies, we will implement a more sophisticated transformer-based model to more effectively classify dialogue.

## References
1. Andernach, T. A machine learning approach to the classification of dialogue
utterances. CoRR cmp-lg/9607022 (1996).
2. Gervits, F., Leuski, A., Bonial, C., Gordon, C., and Traum, D. A classification-
based approach to automating human-robot dialogue. In Increasing Naturalness
and Flexibility in Spoken Dialogue Interaction: 10th International Workshop on
Spoken Dialogue Systems (Singapore, 2021), Springer Singapore, pp. 115–127.
3. Johnson-Roberson, M., Bohg, J., Skantze, G., Gustafson, J., Carlson, R.,
Rasolzadeh, B., and Kragic, D. Enhanced visual scene understanding through
human-robot dialog. pp. 3342–3348.
4. Juluru, K., Shih, H.-H., Keshava Murthy, K. N., and Elnajjar, P. Bag-of-words
technique in natural language processing: A primer for radiologists. RadioGraph-
ics 41, 5 (2021), 1420–1426. PMID: 34388050.
5. Lucignano, L., Cutugno, F., Rossi, S., and Finzi, A. A dialogue system for
multimodal human-robot interaction. In Proceedings of the 15th ACM on Interna-
tional Conference on Multimodal Interaction (New York, NY, USA, 2013), ICMI ’13,
Association for Computing Machinery, p. 197–204.
6. Marge, M., Bonial, C., Lukin, S. M., Hayes, C. J., Foots, A., Artstein, R., Henry,
C., Pollard, K. A., Gordon, C., Gervits, F., Leuski, A., Hill, S. G., Voss, C. R.,
and Traum, D. Balancing efficiency and coverage in human-robot dialogue
collection. In Artificial Intelligence for Human-Robot Interaction (AI-HRI 2018)
(Arlington, Virginia, Oct. 2018), arXiv preprint arXiv:1810.02017.
7. Ray, S. A quick review of machine learning algorithms. 2019 International Confer-
ence on Machine Learning, Big Data, Cloud and Parallel Computing (COMITCon)
(2019), 35–39.
8. Saha, T., Srivastava, S., Firdaus, M., Saha, S., Ekbal, A., and Bhattacharyya,
P. Exploring machine learning and deep learning frameworks for task-oriented
dialogue act classification. In 2019 International Joint Conference on Neural
Networks (IJCNN) (2019), pp. 1–8.
9. Schuurmans, J., and Frasincar, F. Intent classification for dialogue utterances.
IEEE Intelligent Systems 35, 1 (2020), 82–88.
10. Thomason, J., Padmakumar, A., Sinapov, J., Walker, N., Jiang, Y., Yedidsion,
H., Hart, J., Stone, P., and Mooney, R. Jointly improving parsing and perception
for natural language commands through human-robot dialog. Journal of Artificial
Intelligence Research 67 (02 2020), 327–374.
11. Traum, D., Henry, C., Lukin, S., Artstein, R., Gervits, F., Pollard, K., Bonial,
C., Lei, S., Voss, C., Marge, M., Hayes, C., and Hill, S. Dialogue structure
annotation for multi-floor interaction. In Proceedings of the Eleventh International
Conference on Language Resources and Evaluation (LREC 2018) (Miyazaki, Japan,
May 2018), European Language Resources Association (ELRA).
12. Wiriyathammabhum, P., Summers-Stay, D., Fermüller, C., and Aloimonos,
Y. Computer vision and natural language processing: Recent approaches in
multimedia and robotics. ACM Comput. Surv. 49, 4 (dec 2016).

## Acknowledgements
We thank our advisor Dr. Cynthia Matuszek (IRAL) for her generous guidance and support, and Dr. Stephanie Lukin (ARL) for collaborating and sharing the Human-Robot Interaction datasets (SCOUT).
