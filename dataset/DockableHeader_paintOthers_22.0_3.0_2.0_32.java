private void paintOthers(GGlassPane glassPane, Graphics2D g2d, Color background) {

			if (cBounds == null) {
				cBounds = component.getBounds();
				cBounds =
					SwingUtilities.convertRectangle(component.getParent(), cBounds, glassPane);
			}

			double destinationX = cBounds.getCenterX();
			double destinationY = cBounds.getCenterY();

			g2d.setColor(background);
			for (ComponentPaintInfo info : otherComponentInfos) {

				Rectangle b = info.getRelativeBounds(glassPane);
				double scale = 1 - percentComplete;
				int w = (int) (b.width * scale);
				int h = (int) (b.height * scale);

				int offsetX = b.x - ((w - b.width) >> 1);
				int offsetY = b.y - ((h - b.height) >> 1);

				double deltaX = destinationX - offsetX;
				double deltaY = destinationY - offsetY;

				double moveX = percentComplete * deltaX;
				double moveY = percentComplete * deltaY;
				offsetX += moveX;
				offsetY += moveY;

				g2d.drawImage(info.getImage(), offsetX, offsetY, w, h, null);
			}
		}