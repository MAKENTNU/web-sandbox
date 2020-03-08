function ReservationCalendar(element, properties) {
    /**
     * Creates a new ReservationCalendar object. The properties field is a dictionary of properties:
     *
     * machine - The pk of the machine to display for
     * selection - A boolean indicating if selection is allowed
     * canBreakRules - A boolean indicating if the user can break the reservation rules
     * onSelect [optional] - A function to handle what should be shown on selection
     * selectionPopupContent [optional] - A function to generate the content to be shown in the popup made by the
     *                                    default onSelect function.
     */
    this.date = new Date().startOfWeek();
    this.informationHeaders = element.find("thead th").toArray();
    this.days = element.find("tbody .day .reservations").toArray();
    this.element = element;
    this.machine = properties.machine;
    this.selection = properties.selection;
    this.canBreakRules = properties.canBreakRules;
    if (properties.onSelect) {
        this.onSelection = properties.onSelect;
    }
    if (properties.selectionPopupContent) {
        this.selectionPopupContent = properties.selectionPopupContent;
    }
    this.init();
}

ReservationCalendar.prototype.onSelection = function () {
    $(this.element.find(".selection.reservation").first()).popup({
        position: "right center",
        html: this.selectionPopupContent(),
        on: "onload",
    }).popup("show");
};

ReservationCalendar.prototype.selectionPopupContent = function () {
    let dateString;
    let startTime = this.getSelectionStartTime();
    let endTime = this.getSelectionEndTime();
    let calendar = this;

    if (startTime.getDate() === endTime.getDate()) {
        dateString = `${startTime.dateString()} <br/> ${startTime.timeString()} - ${endTime.timeString()}`;
    } else {
        dateString = `${startTime.dateString()} ${startTime.timeString()} - ${endTime.dateString()} ${endTime.timeString()}`;
    }

    let popupContent = $(`
            <div class="ui card">
                <div class="ui content">
                    <div class="header">${gettext("New Reservation")}</div>
                    <div class="description">
                        ${dateString}
                    </div>
                </div>
                <div class="ui bottom attached yellow button">
                    ${gettext("Reserve")}
                </div>
            </div>
    `);

    popupContent.find(".button").on("mousedown touchstart", () => {
        // Create and submit a hidden form to create a new reservation
        let form = $(`<form method='POST' action='${langPrefix}/reservation/make/${calendar.machine}/'>`).appendTo(popupContent);
        $("input[name=csrfmiddlewaretoken]").clone().appendTo(form);
        // Hide the form in case something fails
        $("<input class='make_hidden' name='start_time'>").val(startTime.djangoFormat()).appendTo(form);
        $("<input class='make_hidden' name='end_time'>").val(endTime.djangoFormat()).appendTo(form);
        $("<input class='make_hidden' name='machine_name'>").val(calendar.machine).appendTo(form);
        form.submit();

        return false;
    });

    return popupContent;
};

ReservationCalendar.prototype.init = function () {
    this.update();
    this.element.find(".next.button").click(() => {
        this.date = this.date.nextWeek();
        this.update();
    });

    this.element.find(".current.button").click(() => {
        this.date = new Date().startOfWeek();
        this.update();
    });

    this.element.find(".previous.button").click(() => {
        this.date = this.date.previousWeek();
        this.update();
    });
    let reservationCalendar = this;
    setInterval(() => reservationCalendar.updateCurrentTimeIndication(), 60 * 1000);

    if (this.selection) {
        this.setupSelection();
    }
};

ReservationCalendar.prototype.setupSelection = function () {
    this.selectionStart = null;
    this.selectionEnd = null;
    this.selecting = false;

    let calendar = this;

    for (let day = 0; day < 7; day++) {
        // Start selection when the mouse is clicked
        $(this.days[day]).parent().on("mousedown touchstart", (event) => {
            calendar.selecting = true;
            calendar.selectionStart = calendar.getHoverDate(event, day);
            calendar.selectionEnd = calendar.selectionStart;
            return false;
        }).on("mousemove touchmove", (event) => {
            // Update the selection when any of the days are hovered over
            if (calendar.selecting) {
                calendar.selectionEnd = calendar.getHoverDate(event, day);
                calendar.updateSelection();
            }
        });

        // The header for the week should set the selection date to the start of the week
        $(this.informationHeaders[0]).on("mousemove touchmove", () => {
            if (calendar.selecting) {
                calendar.selectionEnd = calendar.date;
                calendar.updateSelection();
            }
        });

        // The headers above the dates should set the selection date to the start of the given day
        $(this.informationHeaders[day + 2]).on("mousemove touchmove", () => {
            if (calendar.selecting) {
                calendar.selectionEnd = calendar.date.nextDays(day);
                calendar.updateSelection();
            }
        });
    }

    // The part of the calendar that shows the timestamps should set the selection date to the start of the week
    this.element.find(".time.information").on("mousemove touchmove", () => {
        if (calendar.selecting) {
            calendar.selectionEnd = calendar.date;
            calendar.updateSelection();
        }
    });

    // Hovering over the footer will set the selection to the end of the day hovered under
    let footer = this.element.find("tfoot");
    footer.on("mousemove touchmove", (event) => {
        if (calendar.selecting) {
            let hoverPosition = (event.pageX - footer.offset().left) / footer.width();
            let dayHoveredUnder = Math.floor(hoverPosition * 8);
            calendar.selectionEnd = calendar.date.nextDays(dayHoveredUnder);
            calendar.updateSelection();
        }
    });

    // Stop selection whenever the mouse is released
    $(document).on("mouseup touchend", () => {
        if (calendar.selecting) {
            calendar.selecting = false;
            calendar.updateSelection();
            calendar.onSelection();
        }
    });

    $(document).on("mousedown touchstart", () => {
        if (calendar.selecting === false && calendar.selectionStart != null) {
            calendar.resetSelection();
        }
    })
};

ReservationCalendar.prototype.updateSelection = function () {
    let calendar = this;
    if (this.selectionStart != null) {
        let startTime = this.getSelectionStartTime();
        let endTime = this.getSelectionEndTime();
        this.element.find(".selection.reservation").remove();
        this.drawReservation(startTime, endTime, "selection reservation", (element, day) => {
            // If this is the first day of the selection, add the start time indicator
            if (day <= startTime && startTime < day.nextDay()) {
                element.append($(`<div class='selection start time'>${startTime.timeString()}</div>`));

                // Add an element for expanding modifying the selection
                if (!this.selecting) {
                    let expander = $(`<div class='selection expand top'>`);
                    element.append(expander);
                    expander.on("mousedown touchstart", () => {
                        // Modification is done by simply starting the selection anew, now with the selection bound to
                        // the end time
                        calendar.selectionStart = endTime;
                        calendar.selectionEnd = startTime;
                        calendar.selecting = true;
                        calendar.updateSelection();
                        // We don't want to trigger any other events
                        return false;
                    });
                }
            }

            // If this is the last day of the selection, add the end time indicator
            if (day < endTime && endTime <= day.nextDay()) {
                element.append($(`<div class='selection end time'>${endTime.timeString()}</div>`))

                // Add an element for expanding modifying the selection
                if (!this.selecting) {
                    let expander = $(`<div class='selection expand bottom'>`);
                    element.append(expander);
                    expander.on("mousedown touchstart", () => {
                        // Modification is done by simply starting the selection anew, now with the selection bound to
                        // the start time
                        calendar.selectionStart = startTime;
                        calendar.selectionEnd = endTime;
                        calendar.selecting = true;
                        calendar.updateSelection();
                        // We don't want to trigger any other events
                        return false;
                    });
                }
            }
        });
    }
};

ReservationCalendar.prototype.drawReservation = function (startDate, endDate, classes, callback) {
    let date = this.date;
    let millisecondsInDay = 24 * 60 * 60 * 1000;
    for (let day = 0; day < 7; day++) {
        if (endDate > date && startDate < date.nextDay()) {
            let dayStartTime = (Math.max(date, startDate) - date) / millisecondsInDay * 100;
            let dayEndTime = (Math.min(date.nextDay(), endDate) - Math.max(date, startDate)) / millisecondsInDay * 100;
            let reservationBlock = $(`<div class="${classes}" style="top: ${dayStartTime}%; height: ${dayEndTime}%;">`);
            $(this.days[day]).append(reservationBlock);

            if (callback !== undefined) {
                callback(reservationBlock, date);
            }
        }
        date = date.nextDay();
    }
};

ReservationCalendar.prototype.getSelectionStartTime = function () {
    return this.getSelectionTimes()[0];
};

ReservationCalendar.prototype.getSelectionEndTime = function () {
    return this.getSelectionTimes()[1];
};

ReservationCalendar.prototype.getSelectionTimes = function () {
    let startTime = this.roundTime(Math.max(new Date(), Math.min(this.selectionStart, this.selectionEnd)));
    let endTime = this.roundTime(Math.max(new Date(), this.selectionStart, this.selectionEnd));
    let adjusted = true;

    // Adjust the start and end times so that the selection does not overlap any reservations
    while (adjusted) {
        adjusted = false;
        this.reservations.forEach((reservation) => {
            if (reservation.end > startTime && (reservation.start <= startTime || (reservation.end <= endTime && this.selectionStart > reservation.start))) {
                startTime = reservation.end;
                adjusted = true;
            }
            if (reservation.start < endTime && (reservation.end > endTime || (reservation.start >= startTime && this.selectionStart < reservation.end))) {
                endTime = reservation.start;
                adjusted = true;
            }
        });
    }

    if (!this.canBreakRules) {
        // Decrease the end time or increase the start time based on the reservation rules
        if (endTime > this.roundTime(this.selectionStart)) {
            endTime = modifyToFirstValid(this.reservationRules, startTime, endTime, 1);
        } else if (startTime < this.roundTime(this.selectionStart)) {
            startTime = modifyToFirstValid(this.reservationRules, startTime, endTime, 0);
        }
    }

    return [startTime, endTime];
};

ReservationCalendar.prototype.roundTime = function (time) {
    let millisecondsIn5Minutes = 5 * 60 * 1000;
    return new Date(Math.ceil(time / millisecondsIn5Minutes) * millisecondsIn5Minutes);
};

ReservationCalendar.prototype.getHoverDate = function (event, day) {
    let date = this.date.nextDays(day);
    let dayElement = $(event.target).closest(".day");
    let yPosition = event.touches === undefined ? event.pageY : event.touches[0].pageY;
    let timeOfDay = (yPosition - dayElement.offset().top) / dayElement.height();
    date = new Date(date.valueOf() + timeOfDay * 24 * 60 * 60 * 1000);
    return date;
};


ReservationCalendar.prototype.resetSelection = function () {
    if (this.selection) {
        this.selectionStart = null;
        this.selectionEnd = null;
        this.element.find(".selection.reservation").remove();
    }
};

ReservationCalendar.prototype.update = function () {
    this.updateInformationHeaders();
    let calendar = this;

    $.get(`${window.location.origin}/reservation/calendar/${this.machine}/reservations`, {
        startDate: this.date.djangoFormat(),
        endDate: this.date.nextWeek().djangoFormat(),
    }, (data) => calendar.updateReservations.apply(calendar, [data]), "json");

    $.get(`${window.location.origin}/reservation/calendar/${this.machine}/rules`, {}, (data) => {
        calendar.reservationRules = data.rules;
    })
};

ReservationCalendar.prototype.updateCurrentTimeIndication = function () {
    this.element.find(".current.time.indicator").remove();

    let currentTime = new Date();
    if (currentTime >= this.date && currentTime < this.date.nextWeek()) {
        let timeOfDay = (currentTime.getHours() / 24 + currentTime.getMinutes() / (60 * 24) + currentTime.getSeconds() / (60 * 24 * 60)) * 100;
        let timeIndication = $(`<div class="current time indicator" style="top: ${timeOfDay}%;">`);

        $(this.days[(currentTime.getDay() + 6) % 7]).append(timeIndication);
    }
};

ReservationCalendar.prototype.addReservation = function (reservation) {
    reservation.start = new Date(Date.parse(reservation.start));
    reservation.end = new Date(Date.parse(reservation.end));

    this.drawReservation(reservation.start, reservation.end, `${reservation.type} reservation`, (htmlElement) => {
        if (reservation.displayText !== undefined) {
            this.createPopup(htmlElement, reservation);
        }

        if (reservation.eventLink !== undefined) {
            htmlElement.on("click touch", () => {
                window.location = reservation.eventLink;
            })
        }
    });
};

ReservationCalendar.prototype.createPopup = function (reservationElement, reservation) {
    let content;

    if (reservation.user !== undefined) {
        let duration = `${reservation.start.getDayTextShort()} ${reservation.start.timeString()} - ${reservation.end.getDayTextShort()} ${reservation.end.timeString()}`;

        content = `
            <div class="header">${gettext("Reservation")}</div>
            <div><b>${gettext("Name")}:</b> ${reservation.user}</div>
            <div><b>${gettext("Email")}:</b> ${reservation.email}</div>
            <div><b>${gettext("Time")}:</b> ${duration}</div>
        `;

        if (reservation.displayText !== "") {
            content += `<div><b>${gettext("Comment")}:</b></div><div>${reservation.displayText}</div>`
        }
    } else if (reservation.eventLink !== undefined) {
        content = `<div class="header">${reservation.displayText}</div>`;
    } else {
        content = reservation.displayText;
    }

    reservationElement.popup({
        position: "top center",
        html: content,
    });

};

ReservationCalendar.prototype.updateReservations = function (data) {
    this.days.forEach(day => $(day).empty());
    this.updateCurrentTimeIndication();

    let reservationCalendar = this;
    data.reservations.forEach((reservation) => reservationCalendar.addReservation.apply(reservationCalendar, [reservation]));

    this.reservations = data.reservations;
    this.resetSelection();
};

ReservationCalendar.prototype.updateInformationHeaders = function () {
    this.informationHeaders[0].querySelector(".large.header").textContent = this.date.getMonthText();
    this.informationHeaders[0].querySelector(".medium.header").textContent = this.date.getWeekNumber();
    this.informationHeaders[1].querySelector(".large.header").textContent = this.date.getMonthTextShort();
    this.informationHeaders[1].querySelector(".medium.header").textContent = this.date.getWeekNumber();

    let date = this.date;
    for (let day = 2; day < 9; day++) {
        this.informationHeaders[day].querySelector(".medium.header").textContent = date.getDate();
        date = date.nextDay();
    }
};