
![RT-MESI Protocol – State Transaction Diagram](imgs/state_digram.svg)

## Наш вариант

Протокол: **RT-MESI**   
Политика замещения: **MRU**

## Ссылки

 - Код Айзека и Пети:  
https://github.com/MathematicLove/PetyaAndAyzek_Num2_ArchSuperGavnoEVM/tree/main

 - Базовый видос про кэш:  
https://youtu.be/7n_8cOBpQrg?si=160F3EyU1Zb13mAA

 - Ссылка на вики про **RT-MESI**:  
https://en.wikipedia.org/wiki/Cache_coherency_protocols_(examples)#RT-MESI_protocol

 - Ссылки на патенты:  
    - https://worldwide.espacenet.com/patent/search/family/021821486/publication/US6275908B1?q=pn%3DUS6275908
    - https://worldwide.espacenet.com/patent/search/family/021820362/publication/US6334172B1?q=pn%3DUS6334172

 - Эталон:  
  https://www.scss.tcd.ie/Jeremy.Jones/vivio/caches/MESIHelp.htm

## Запуск
Из корня проекта
```cmd
python app.py
```

## Сборка
Предварительно устанавливаем [auto-py-to-exe](https://github.com/brentvollebregt/auto-py-to-exe)
```cmd
pip install auto-py-to-exe
```

Из корня проекта выполняем
```cmd
pyinstaller --noconfirm --onefile --windowed app.py
```

## Текст задания
Всем студентам необходимо распределиться на максимум 16 рабочих групп (состав группы — от 4 до 6 человек), для распределения принадлежность потенциальных участников одной рабочей группы к одной или разным учебным группам не важна. Рабочие группы должны будут поделить между собой предложенные варианты таким образом, чтобы один вариант достался не более чем одной рабочей группе, работа двух рабочих групп над одним вариантом не допускается — в таком случае обе рабочие группы не получат аттестацию по этому заданию.

Каждый вариант представляет собой сочетание протокола кэш-когерентности и политики замещения из приведённого перечня (см. вложение), отмеченное в соответствующей клетке символом «+». Другие сочетания использовать не нужно — такие работы не будут проверяться.

Что нужно сделать? Реализовать модель, демонстрирующую работу подсистемы памяти в симметричной многопроцессорной системе. В качестве эталона можно использовать такой демонстратор: https://www.scss.tcd.ie/Jeremy.Jones/vivio/caches/MESIHelp.htm — здесь показана работа протокола MESI с кэшем прямого отображения и без политик замещения.

Условия вашей работы более сложные:
1) протокол кэш-когерентности и политика замещения определяются выбранным вариантом;
2) число процессоров в системе — 4;
3) объем основной памяти — 16 адресуемых ячеек по 1 байт;
4) размер строки памяти и кэша — 1 байт;
5) число строк кэша — 4;
6) ассоциативность кэша — 2.

Все необходимые атрибуты для фиксации и обновления времени последнего обращения к строке или частоты обращения к ней вы определяете самостоятельно, единицей времени во всех случаях является такт машинного времени.

Модель обязательно должна отображать:
1) содержимое и адрес каждой ячейки основной памяти;
2) тэг, данные и состояние каждой строки кэша (возможные состояния определяются протоколом из вашего варианта);
3) счётчик метрики политики замещения для каждой строки кэша;
4) запросы по шинам адреса, данных, состояний и ответы на них (схематично, как в эталонной модели, без комментирования каждого запроса и ответа);
5) общий счётчик тактов машинного времени с момента запуска или сброса.

Команды управления, принимаемые от пользователя: для каждого процессора операции чтения и записи памяти по указанному (выбранному) адресу, общий сброс состояния модели, возможность «продвижения» по тактам вручную. Обратите внимание, что в эталонной модели реализована возможность выполнять операции на нескольких процессорах одновременно — в вашей модели это тоже должно быть реализовано. Начальное состояние кэшей — все строки пусты, начальное состояние памяти — все ячейки содержат значение «0». По аналогии с эталонной моделью операция записи выполняет инкремент значения на «1».

Языки программирования, фрэймворки, средства визуализации — любые, лишь бы я мог запустить ваше приложение на своём рабочем ПК. Если для этого потребуется какое-то дополнительно ПО — лучше будет собрать всё в виде образа виртуальной машины или контейнера. Красивая анимация, раскрашивание и другие декорации не требуются и не принимаются в расчёт при оценивании работы.

Работа должна сопровождаться отчётом. В отчёте, помимо содержательной части, должно быть указано распределение задач по участникам рабочей группы (это можно сделать в заключении или в приложении).

Крайний срок приёма работы — 18.04.2024 23:59, но примерно за неделю-полторы до этого срока необходимо будет предоставить информацию о выполнении работы. Для этого мы согласуем очные встречи.

Также предлагаю вам достаточно оперативно определиться с составами рабочих групп и распределением вариантов, чтобы как можно скорее начать первичный анализ исходных данных и сформулировать первые уточняющие вопросы. Для ответов на них и более интерактивного обсуждения возможно будет согласовать очные встречи в самое ближайшее время.
